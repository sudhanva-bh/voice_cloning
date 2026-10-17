#include "euler_sampler.h"
#include <cmath>
#include <cstring>
#include <iostream>
#include <string>
#include <algorithm>
#include <android/log.h>

#define TAG "EulerSampler"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

namespace indic {

std::vector<float> EulerSampler::computeSwaySchedule(int num_steps, float sway_coef) const {
    std::vector<float> schedule(num_steps + 1);
    for (int i = 0; i <= num_steps; ++i) {
        float t = static_cast<float>(i) / num_steps;
        // Cosine sway: t + sway * (cos(pi/2 * t) - 1 + t)
        float sway = sway_coef * (std::cos(static_cast<float>(M_PI) / 2.0f * t) - 1.0f + t);
        schedule[i] = t + sway;
    }
    return schedule;
}

bool EulerSampler::sample(
    TfLiteInterpreter* dit_interp,
    const float* cond_mel,
    const int32_t* text_tokens,
    float* mel_out,
    int num_steps,
    float cfg_strength,
    float sway_coef,
    uint32_t seed
) {
    if (!dit_interp) return false;

    // 1. Initialize Gaussian noise x_0 ~ N(0, 1)
    std::mt19937 gen(seed);
    std::normal_distribution<float> dist(0.0f, 1.0f);
    for (size_t i = 0; i < LATENT_ELEMENTS; ++i) {
        mel_out[i] = dist(gen);
    }

    // 2. Prepare null inputs for classifier-free guidance
    std::vector<float> null_cond(LATENT_ELEMENTS, 0.0f);
    std::vector<int32_t> null_text(TEXT_LEN, -1);

    // Buffers for velocity field predictions
    std::vector<float> v_cond(LATENT_ELEMENTS);

    // 3. Compute time schedule
    std::vector<float> t_steps = computeSwaySchedule(num_steps, sway_coef);

    // 4. Bind input/output tensor references directly from the pre-allocated interpreter.
    //
    //    IMPORTANT: We do NOT use TfLiteSignatureRunner here. Calling
    //    TfLiteSignatureRunnerAllocateTensors() after the interpreter has already been
    //    fully allocated (in LiteRTIndicEngine::initializeFromFiles) triggers a second
    //    arena allocation cycle that resets internal constant tensor arena pointers,
    //    causing the "Input tensor 402 lacks data" error for arith.constant46 (~1.24 MB
    //    INT8 weight tensor, alloc_type=kTfLiteArenaRw, data=0x0 after 2nd allocation).
    //    We bypass SignatureRunner entirely and use raw interpreter tensor access,
    //    relying on the arena that was already committed at engine initialization.

    int raw_in_count = TfLiteInterpreterGetInputTensorCount(dit_interp);
    LOGI("Raw interpreter input count: %d", raw_in_count);

    TfLiteTensor* in_x    = nullptr;
    TfLiteTensor* in_cond = nullptr;
    TfLiteTensor* in_text = nullptr;
    TfLiteTensor* in_t    = nullptr;
    const TfLiteTensor* out_v = nullptr;

    for (int i = 0; i < raw_in_count; ++i) {
        TfLiteTensor* t = TfLiteInterpreterGetInputTensor(dit_interp, i);
        if (!t) continue;
        const char* name = TfLiteTensorName(t);
        size_t bytes     = TfLiteTensorByteSize(t);
        void*  data_ptr  = TfLiteTensorData(t);
        LOGI("Raw interp input[%d]: name='%s', bytes=%zu, data=%p",
             i, name ? name : "null", bytes, data_ptr);
    }

    // The DiT model exposes 4 inputs in fixed order (verified in Phase 5 logcat):
    //   [0] serving_default_args_0 - x (noisy mel)   [1, FRAMES, MEL_BINS] float32  204800 bytes
    //   [1] serving_default_args_1 - cond_mel         [1, FRAMES, MEL_BINS] float32  204800 bytes
    //   [2] serving_default_args_2 - text_tokens      [1, TEXT_LEN]          int32      512 bytes
    //   [3] serving_default_args_3 - t (time scalar)  [1]                    float32      4 bytes
    int raw_out_count = TfLiteInterpreterGetOutputTensorCount(dit_interp);
    LOGI("Raw interpreter output count: %d", raw_out_count);

    if (raw_in_count >= 4) {
        in_x    = TfLiteInterpreterGetInputTensor(dit_interp, 0);
        in_cond = TfLiteInterpreterGetInputTensor(dit_interp, 1);
        in_text = TfLiteInterpreterGetInputTensor(dit_interp, 2);
        in_t    = TfLiteInterpreterGetInputTensor(dit_interp, 3);
    }
    if (raw_out_count >= 1) {
        out_v   = TfLiteInterpreterGetOutputTensor(dit_interp, 0);
    }

    // Validate all tensor handles and that their data buffers are live (non-null)
    if (!in_x || !in_cond || !in_text || !in_t || !out_v) {
        LOGE("Failed to access all DiT interpreter tensors (handles null)");
        return false;
    }
    if (!TfLiteTensorData(in_x) || !TfLiteTensorData(in_cond) ||
        !TfLiteTensorData(in_text) || !TfLiteTensorData(in_t)) {
        LOGE("One or more DiT input tensor data pointers are null - arena not allocated");
        return false;
    }

    LOGI("out_v tensor details: name='%s', bytes=%zu, type=%d, num_dims=%d, shape=[%d, %d, %d]",
         TfLiteTensorName(out_v), TfLiteTensorByteSize(out_v), TfLiteTensorType(out_v),
         TfLiteTensorNumDims(out_v),
         TfLiteTensorDim(out_v, 0), TfLiteTensorDim(out_v, 1),
         TfLiteTensorNumDims(out_v) > 2 ? TfLiteTensorDim(out_v, 2) : -1);

    LOGI("Tensor bindings OK: in_x=%p(%zu) in_cond=%p(%zu) in_text=%p(%zu) in_t=%p(%zu) out_v=%p(%zu)",
         TfLiteTensorData(in_x),    TfLiteTensorByteSize(in_x),
         TfLiteTensorData(in_cond), TfLiteTensorByteSize(in_cond),
         TfLiteTensorData(in_text), TfLiteTensorByteSize(in_text),
         TfLiteTensorData(in_t),    TfLiteTensorByteSize(in_t),
         TfLiteTensorData(const_cast<TfLiteTensor*>(out_v)),
         TfLiteTensorByteSize(out_v));

    // 5. Continuous Flow Matching Loop
    for (int step = 0; step < num_steps; ++step) {
        float t_val = t_steps[step];
        float dt    = t_steps[step + 1] - t_steps[step];

        if (step == 0) {
            LOGI("Step 0 inputs: mel_out[0..4]=[%.3f, %.3f, %.3f, %.3f, %.3f], cond_mel[0..4]=[%.3f, %.3f, %.3f, %.3f, %.3f], text[0..4]=[%d, %d, %d, %d, %d], t_val=%.4f",
                 mel_out[0], mel_out[1], mel_out[2], mel_out[3], mel_out[4],
                 cond_mel[0], cond_mel[1], cond_mel[2], cond_mel[3], cond_mel[4],
                 text_tokens[0], text_tokens[1], text_tokens[2], text_tokens[3], text_tokens[4],
                 t_val);
        }

        // --- Conditioned Pass ---
        TfLiteStatus s_x    = TfLiteTensorCopyFromBuffer(in_x,    mel_out,     LATENT_ELEMENTS * sizeof(float));
        TfLiteStatus s_cond = TfLiteTensorCopyFromBuffer(in_cond, cond_mel,    LATENT_ELEMENTS * sizeof(float));
        TfLiteStatus s_text = TfLiteTensorCopyFromBuffer(in_text, text_tokens, TEXT_LEN        * sizeof(int32_t));
        TfLiteStatus s_t    = TfLiteTensorCopyFromBuffer(in_t,    &t_val,      sizeof(float));

        if (s_x != kTfLiteOk || s_cond != kTfLiteOk || s_text != kTfLiteOk || s_t != kTfLiteOk) {
            LOGE("CopyFromBuffer failed at step %d: s_x=%d s_cond=%d s_text=%d s_t=%d",
                 step, s_x, s_cond, s_text, s_t);
            return false;
        }

        TfLiteStatus inv_status = TfLiteInterpreterInvoke(dit_interp);
        if (inv_status != kTfLiteOk) {
            LOGE("DiT conditioned invoke failed at step %d", step);
            return false;
        }

        TfLiteTensorCopyToBuffer(out_v, v_cond.data(), LATENT_ELEMENTS * sizeof(float));

        // --- Unconditioned Pass (Classifier-Free Guidance) ---
        TfLiteTensorCopyFromBuffer(in_cond, null_cond.data(), LATENT_ELEMENTS * sizeof(float));
        TfLiteTensorCopyFromBuffer(in_text, null_text.data(), TEXT_LEN        * sizeof(int32_t));
        // in_x and in_t are unchanged from conditioned pass

        TfLiteStatus null_status = TfLiteInterpreterInvoke(dit_interp);
        if (null_status != kTfLiteOk) {
            LOGE("DiT null invoke failed at step %d", step);
            return false;
        }
        std::vector<float> v_null(LATENT_ELEMENTS);
        TfLiteTensorCopyToBuffer(out_v, v_null.data(), LATENT_ELEMENTS * sizeof(float));

        if (step == 0) {
            LOGI("Step 0 unconditioned v_null[0..4]=[%.3f, %.3f, %.3f, %.3f, %.3f]",
                 v_null[0], v_null[1], v_null[2], v_null[3], v_null[4]);
        }

        // --- Vector Field Combination & Euler Step ---
        // v = v_cond + (v_cond - v_null) * cfg
        // x = x + dt * v
        float norm_vc = 0.0f, norm_vn = 0.0f, norm_v = 0.0f;
        int nan_vc_cnt = 0, nan_vn_cnt = 0;
        for (size_t i = 0; i < LATENT_ELEMENTS; ++i) {
            float vc = v_cond[i];
            float vn = v_null[i];
            if (std::isnan(vc)) nan_vc_cnt++;
            if (std::isnan(vn)) nan_vn_cnt++;
            float v  = vc + (vc - vn) * cfg_strength;
            mel_out[i] += dt * v;
            norm_vc += vc * vc;
            norm_vn += vn * vn;
            norm_v  += v * v;
        }
        LOGI("[EulerSampler] Step %d/%d (t=%.3f, dt=%.3f): |vc|=%.2f (nans=%d), |vn|=%.2f (nans=%d), |v|=%.2f",
             step + 1, num_steps, t_val, dt,
             std::sqrt(norm_vc), nan_vc_cnt, std::sqrt(norm_vn), nan_vn_cnt, std::sqrt(norm_v));
    }

    return true;
}

} // namespace indic
