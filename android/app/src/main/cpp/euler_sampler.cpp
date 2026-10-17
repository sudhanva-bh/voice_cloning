#include "euler_sampler.h"
#include <cmath>
#include <cstring>
#include <iostream>

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

    // 4. Fetch tensor references
    TfLiteTensor* in_x = TfLiteInterpreterGetInputTensor(dit_interp, 0);
    TfLiteTensor* in_cond = TfLiteInterpreterGetInputTensor(dit_interp, 1);
    TfLiteTensor* in_text = TfLiteInterpreterGetInputTensor(dit_interp, 2);
    TfLiteTensor* in_t = TfLiteInterpreterGetInputTensor(dit_interp, 3);
    const TfLiteTensor* out_v = TfLiteInterpreterGetOutputTensor(dit_interp, 0);

    if (!in_x || !in_cond || !in_text || !in_t || !out_v) {
        std::cerr << "[EulerSampler] Failed to access DiT interpreter tensors" << std::endl;
        return false;
    }

    // 5. Continuous Flow Matching Loop
    for (int step = 0; step < num_steps; ++step) {
        float t_val = t_steps[step];
        float dt = t_steps[step + 1] - t_steps[step];

        // --- Conditioned Pass ---
        TfLiteTensorCopyFromBuffer(in_x, mel_out, LATENT_ELEMENTS * sizeof(float));
        TfLiteTensorCopyFromBuffer(in_cond, cond_mel, LATENT_ELEMENTS * sizeof(float));
        TfLiteTensorCopyFromBuffer(in_text, text_tokens, TEXT_LEN * sizeof(int32_t));
        TfLiteTensorCopyFromBuffer(in_t, &t_val, sizeof(float));

        if (TfLiteInterpreterInvoke(dit_interp) != kTfLiteOk) {
            std::cerr << "[EulerSampler] DiT conditioned invoke failed at step " << step << std::endl;
            return false;
        }
        TfLiteTensorCopyToBuffer(out_v, v_cond.data(), LATENT_ELEMENTS * sizeof(float));

        // --- Unconditioned Pass (Classifier-Free Guidance) ---
        TfLiteTensorCopyFromBuffer(in_cond, null_cond.data(), LATENT_ELEMENTS * sizeof(float));
        TfLiteTensorCopyFromBuffer(in_text, null_text.data(), TEXT_LEN * sizeof(int32_t));
        // in_x and in_t are unchanged

        if (TfLiteInterpreterInvoke(dit_interp) != kTfLiteOk) {
            std::cerr << "[EulerSampler] DiT null invoke failed at step " << step << std::endl;
            return false;
        }
        const float* v_null_ptr = reinterpret_cast<const float*>(TfLiteTensorData(out_v));

        // --- Vector Field Combination & Euler Step ---
        // v = v_cond + (v_cond - v_null) * cfg
        // x = x + dt * v
        #pragma omp parallel for simd
        for (size_t i = 0; i < LATENT_ELEMENTS; ++i) {
            float vc = v_cond[i];
            float vn = v_null_ptr[i];
            float v = vc + (vc - vn) * cfg_strength;
            mel_out[i] += dt * v;
        }
    }

    return true;
}

} // namespace indic
