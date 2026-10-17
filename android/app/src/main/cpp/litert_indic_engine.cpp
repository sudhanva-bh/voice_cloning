#include "litert_indic_engine.h"
#include <chrono>
#include <iostream>
#include <fstream>
#include <cmath>
#include <cstring>
#include <android/log.h>

#define TAG "LiteRTIndicNative"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

namespace indic {

LiteRTIndicEngine::LiteRTIndicEngine() = default;

LiteRTIndicEngine::~LiteRTIndicEngine() {
    if (dit_interp_) TfLiteInterpreterDelete(dit_interp_);
    if (dit_xnnpack_delegate_) TfLiteXNNPackDelegateDelete(dit_xnnpack_delegate_);
    if (dit_model_) TfLiteModelDelete(dit_model_);

    if (vocos_interp_) TfLiteInterpreterDelete(vocos_interp_);
    if (vocos_xnnpack_delegate_) TfLiteXNNPackDelegateDelete(vocos_xnnpack_delegate_);
    if (vocos_model_) TfLiteModelDelete(vocos_model_);
}

bool LiteRTIndicEngine::initialize(
    const void* dit_model_data, size_t dit_model_size,
    const void* vocos_model_data, size_t vocos_model_size,
    const char* vocab_data, size_t vocab_size,
    int num_threads
) {
    num_threads_ = num_threads;

    // 1. Load Tokenizer
    if (!tokenizer_.loadFromBuffer(vocab_data, vocab_size)) {
        std::cerr << "[LiteRTIndicEngine] Failed to load vocabulary" << std::endl;
        return false;
    }

    // 2. Initialize DiT Interpreter
    dit_model_ = TfLiteModelCreate(dit_model_data, dit_model_size);
    if (!dit_model_) {
        std::cerr << "[LiteRTIndicEngine] Failed to create DiT model" << std::endl;
        return false;
    }

    TfLiteInterpreterOptions* dit_options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreterOptionsSetNumThreads(dit_options, num_threads_);
    dit_interp_ = TfLiteInterpreterCreate(dit_model_, dit_options);
    TfLiteInterpreterOptionsDelete(dit_options);

    if (!dit_interp_) {
        std::cerr << "[LiteRTIndicEngine] Failed to create DiT interpreter" << std::endl;
        return false;
    }

    int dit_dims_mel[] = {1, EulerSampler::FRAMES, EulerSampler::MEL_BINS};
    int dit_dims_text[] = {1, EulerSampler::TEXT_LEN};
    int dit_dims_t[] = {1};

    TfLiteInterpreterResizeInputTensor(dit_interp_, 0, dit_dims_mel, 3);
    TfLiteInterpreterResizeInputTensor(dit_interp_, 1, dit_dims_mel, 3);
    TfLiteInterpreterResizeInputTensor(dit_interp_, 2, dit_dims_text, 2);
    TfLiteInterpreterResizeInputTensor(dit_interp_, 3, dit_dims_t, 1);

    if (TfLiteInterpreterAllocateTensors(dit_interp_) != kTfLiteOk) {
        std::cerr << "[LiteRTIndicEngine] Failed to allocate DiT tensors" << std::endl;
        return false;
    }

    // 3. Initialize Vocos Interpreter
    vocos_model_ = TfLiteModelCreate(vocos_model_data, vocos_model_size);
    if (!vocos_model_) {
        std::cerr << "[LiteRTIndicEngine] Failed to create Vocos model" << std::endl;
        return false;
    }

    TfLiteInterpreterOptions* vocos_options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreterOptionsSetNumThreads(vocos_options, num_threads_);
    vocos_interp_ = TfLiteInterpreterCreate(vocos_model_, vocos_options);
    TfLiteInterpreterOptionsDelete(vocos_options);

    if (!vocos_interp_) {
        std::cerr << "[LiteRTIndicEngine] Failed to create Vocos interpreter" << std::endl;
        return false;
    }

    int voc_dims[] = {1, EulerSampler::MEL_BINS, EulerSampler::FRAMES};
    TfLiteInterpreterResizeInputTensor(vocos_interp_, 0, voc_dims, 3);

    if (TfLiteInterpreterAllocateTensors(vocos_interp_) != kTfLiteOk) {
        std::cerr << "[LiteRTIndicEngine] Failed to allocate Vocos tensors" << std::endl;
        return false;
    }

    ready_ = true;
    return true;
}

bool LiteRTIndicEngine::initializeFromFiles(
    const std::string& dit_model_path,
    const std::string& vocos_model_path,
    const std::string& vocab_path,
    int num_threads
) {
    num_threads_ = num_threads;

    // 1. Load Tokenizer from file
    std::ifstream vfile(vocab_path);
    if (!vfile.is_open()) {
        std::cerr << "[LiteRTIndicEngine] Failed to open vocab file: " << vocab_path << std::endl;
        return false;
    }
    std::string vcontent((std::istreambuf_iterator<char>(vfile)), std::istreambuf_iterator<char>());
    if (!tokenizer_.loadFromBuffer(vcontent.data(), vcontent.size())) {
        std::cerr << "[LiteRTIndicEngine] Failed to parse vocab from file" << std::endl;
        return false;
    }

    // 2. Initialize DiT Interpreter from file
    dit_model_ = TfLiteModelCreateFromFile(dit_model_path.c_str());
    if (!dit_model_) {
        std::cerr << "[LiteRTIndicEngine] Failed to create DiT model from file: " << dit_model_path << std::endl;
        return false;
    }

    TfLiteInterpreterOptions* dit_options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreterOptionsSetNumThreads(dit_options, num_threads_);
    dit_interp_ = TfLiteInterpreterCreate(dit_model_, dit_options);
    TfLiteInterpreterOptionsDelete(dit_options);

    if (!dit_interp_) {
        LOGE("[LiteRTIndicEngine] Failed to create DiT interpreter from file");
        return false;
    }

    // Explicitly resize dynamic input tensors to concrete shapes first.
    // XNNPACK requires concrete dimensions to build its execution plan.
    int dit_dims_mel[] = {1, EulerSampler::FRAMES, EulerSampler::MEL_BINS}; // [1, 512, 100]
    int dit_dims_text[] = {1, EulerSampler::TEXT_LEN};                      // [1, 128]
    int dit_dims_t[] = {1};                                                  // [1]

    TfLiteStatus s0 = TfLiteInterpreterResizeInputTensor(dit_interp_, 0, dit_dims_mel, 3);
    TfLiteStatus s1 = TfLiteInterpreterResizeInputTensor(dit_interp_, 1, dit_dims_mel, 3);
    TfLiteStatus s2 = TfLiteInterpreterResizeInputTensor(dit_interp_, 2, dit_dims_text, 2);
    TfLiteStatus s3 = TfLiteInterpreterResizeInputTensor(dit_interp_, 3, dit_dims_t, 1);
    LOGI("[LiteRTIndicEngine] DiT ResizeInputTensor status: s0=%d, s1=%d, s2=%d, s3=%d", s0, s1, s2, s3);

    // CRITICAL FIX (Phase 5 root cause resolved):
    // TfLiteInterpreterModifyGraphWithDelegate() internally calls AllocateTensors().
    // If AllocateTensors() is called AGAIN afterwards it performs a second arena
    // allocation cycle that resets the data pointer of kTfLiteArenaRw constant
    // tensors (e.g. arith.constant46 / tensor 402, ~1.24 MB INT8) to 0x0, causing
    // "Input tensor 402 lacks data" on the first Invoke().
    //
    // Correct sequence:
    //   1. Resize → 2. ModifyGraphWithDelegate (does AllocateTensors internally) → DONE
    //   If delegate fails → fall back to CPU → call AllocateTensors() manually.
    //   Never call AllocateTensors() after a SUCCESSFUL ModifyGraphWithDelegate.
    {
        TfLiteXNNPackDelegateOptions xnnpack_opts = TfLiteXNNPackDelegateOptionsDefault();
        xnnpack_opts.num_threads = num_threads_;
        dit_xnnpack_delegate_ = TfLiteXNNPackDelegateCreate(&xnnpack_opts);
    }

    bool dit_delegate_ok = false;
    if (dit_xnnpack_delegate_) {
        TfLiteStatus del_status = TfLiteInterpreterModifyGraphWithDelegate(dit_interp_, dit_xnnpack_delegate_);
        LOGI("[LiteRTIndicEngine] DiT ModifyGraphWithDelegate returned %d", del_status);
        if (del_status == kTfLiteOk) {
            // ModifyGraphWithDelegate ran AllocateTensors internally — do NOT call again.
            dit_delegate_ok = true;
            LOGI("[LiteRTIndicEngine] DiT tensors allocated via XNNPACK delegate (skipping extra AllocateTensors)");
        } else {
            LOGW("[LiteRTIndicEngine] DiT delegate modify failed; falling back to CPU-only interpreter");
            TfLiteXNNPackDelegateDelete(dit_xnnpack_delegate_);
            dit_xnnpack_delegate_ = nullptr;
            // Recreate a clean interpreter (delegate contaminated the previous one)
            TfLiteInterpreterDelete(dit_interp_);
            TfLiteInterpreterOptions* clean_opts = TfLiteInterpreterOptionsCreate();
            TfLiteInterpreterOptionsSetNumThreads(clean_opts, num_threads_);
            dit_interp_ = TfLiteInterpreterCreate(dit_model_, clean_opts);
            TfLiteInterpreterOptionsDelete(clean_opts);
            TfLiteInterpreterResizeInputTensor(dit_interp_, 0, dit_dims_mel, 3);
            TfLiteInterpreterResizeInputTensor(dit_interp_, 1, dit_dims_mel, 3);
            TfLiteInterpreterResizeInputTensor(dit_interp_, 2, dit_dims_text, 2);
            TfLiteInterpreterResizeInputTensor(dit_interp_, 3, dit_dims_t, 1);
        }
    }

    TfLiteStatus alloc_status = TfLiteInterpreterAllocateTensors(dit_interp_);
    if (alloc_status != kTfLiteOk) {
        LOGE("[LiteRTIndicEngine] Failed to allocate DiT tensors from file (status=%d)", alloc_status);
        return false;
    }
    LOGI("[LiteRTIndicEngine] DiT tensors allocated successfully");

    TfLiteStatus r_status = TfLiteInterpreterResetVariableTensors(dit_interp_);
    LOGI("[LiteRTIndicEngine] TfLiteInterpreterResetVariableTensors returned status=%d", r_status);

    // 3. Initialize Vocos Interpreter from file
    vocos_model_ = TfLiteModelCreateFromFile(vocos_model_path.c_str());
    if (!vocos_model_) {
        LOGE("[LiteRTIndicEngine] Failed to create Vocos model from file: %s", vocos_model_path.c_str());
        return false;
    }

    TfLiteInterpreterOptions* vocos_options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreterOptionsSetNumThreads(vocos_options, num_threads_);
    vocos_interp_ = TfLiteInterpreterCreate(vocos_model_, vocos_options);
    TfLiteInterpreterOptionsDelete(vocos_options);

    if (!vocos_interp_) {
        LOGE("[LiteRTIndicEngine] Failed to create Vocos interpreter from file");
        return false;
    }

    // Resize Vocos input mel: [1, 100, 512]
    int voc_dims[] = {1, EulerSampler::MEL_BINS, EulerSampler::FRAMES};
    TfLiteInterpreterResizeInputTensor(vocos_interp_, 0, voc_dims, 3);

    {
        TfLiteXNNPackDelegateOptions xnnpack_opts = TfLiteXNNPackDelegateOptionsDefault();
        xnnpack_opts.num_threads = num_threads_;
        vocos_xnnpack_delegate_ = TfLiteXNNPackDelegateCreate(&xnnpack_opts);
    }

    if (vocos_xnnpack_delegate_) {
        TfLiteStatus voc_del_status = TfLiteInterpreterModifyGraphWithDelegate(vocos_interp_, vocos_xnnpack_delegate_);
        LOGI("[LiteRTIndicEngine] Vocos ModifyGraphWithDelegate returned %d", voc_del_status);
        if (voc_del_status != kTfLiteOk) {
            LOGW("[LiteRTIndicEngine] Vocos delegate modify failed; falling back to clean CPU interpreter");
            TfLiteXNNPackDelegateDelete(vocos_xnnpack_delegate_);
            vocos_xnnpack_delegate_ = nullptr;
            TfLiteInterpreterDelete(vocos_interp_);
            TfLiteInterpreterOptions* clean_opts = TfLiteInterpreterOptionsCreate();
            TfLiteInterpreterOptionsSetNumThreads(clean_opts, num_threads_);
            vocos_interp_ = TfLiteInterpreterCreate(vocos_model_, clean_opts);
            TfLiteInterpreterOptionsDelete(clean_opts);
            TfLiteInterpreterResizeInputTensor(vocos_interp_, 0, voc_dims, 3);
        }
    }

    if (TfLiteInterpreterAllocateTensors(vocos_interp_) != kTfLiteOk) {
        LOGE("[LiteRTIndicEngine] Failed to allocate Vocos tensors from file");
        return false;
    }
    LOGI("[LiteRTIndicEngine] Vocos tensors allocated successfully");

    ready_ = true;
    return true;
}


std::vector<float> LiteRTIndicEngine::synthesize(
    const float* ref_pcm, size_t ref_pcm_samples,
    const std::string& ref_text,
    const std::string& target_text,
    int num_steps,
    float cfg_strength,
    uint32_t seed,
    EngineTelemetry* out_telemetry
) {
    if (!ready_) return {};

    auto t_start = std::chrono::high_resolution_clock::now();

    // 1. Extract reference Mel Spectrogram
    std::vector<float> ref_mel(AudioProcessor::MAX_FRAMES * AudioProcessor::N_MELS, 0.0f);
    int ref_frames = audio_proc_.extractMel(ref_pcm, ref_pcm_samples, ref_mel.data(), AudioProcessor::MAX_FRAMES);

    auto t_mel = std::chrono::high_resolution_clock::now();

    // 2. Duration allocation
    size_t ref_char_len = std::max<size_t>(ref_text.length(), 1);
    size_t gen_char_len = std::max<size_t>(target_text.length(), 1);
    int gen_frames = static_cast<int>(static_cast<float>(ref_frames) / ref_char_len * gen_char_len * 1.05f);
    int total_frames = std::min(ref_frames + gen_frames, AudioProcessor::MAX_FRAMES);
    gen_frames = total_frames - ref_frames;

    // 3. Prepare conditioning mel and tokens
    std::vector<float> cond_mel(EulerSampler::LATENT_ELEMENTS, 0.0f);
    std::memcpy(cond_mel.data(), ref_mel.data(), ref_frames * AudioProcessor::N_MELS * sizeof(float));

    std::string full_text = ref_text + " " + target_text;
    std::vector<int32_t> text_tokens = tokenizer_.encode(full_text, EulerSampler::TEXT_LEN, -1);

    // 4. Run CFM Euler ODE Sampler
    std::vector<float> mel_out(EulerSampler::LATENT_ELEMENTS);
    bool sample_ok = euler_sampler_.sample(
        dit_interp_,
        cond_mel.data(),
        text_tokens.data(),
        mel_out.data(),
        num_steps,
        cfg_strength,
        -1.0f, // sway_coef
        seed
    );
    if (!sample_ok) {
        LOGE("EulerSampler failed to complete CFM ODE steps");
        return {};
    }

    auto t_diff = std::chrono::high_resolution_clock::now();

    // 5. Vocos Neural Vocoding
    // Invert conditioning portion: replace generated ref_frames with ground-truth ref_mel
    std::memcpy(mel_out.data(), ref_mel.data(), ref_frames * AudioProcessor::N_MELS * sizeof(float));

    // Transpose mel from [512, 100] (time, mel) to Vocos input layout [1, 100, 512] (mel, time)
    int voc_in_count = TfLiteInterpreterGetInputTensorCount(vocos_interp_);
    LOGI("Vocos total input tensors: %d", voc_in_count);
    TfLiteTensor* voc_in = TfLiteInterpreterGetInputTensor(vocos_interp_, 0);
    if (voc_in) {
        LOGI("Vocos input [0]: name='%s', bytes=%zu", TfLiteTensorName(voc_in), TfLiteTensorByteSize(voc_in));
    }
    std::vector<float> voc_in_buf(AudioProcessor::N_MELS * AudioProcessor::MAX_FRAMES);

    for (int t = 0; t < AudioProcessor::MAX_FRAMES; ++t) {
        for (int m = 0; m < AudioProcessor::N_MELS; ++m) {
            voc_in_buf[m * AudioProcessor::MAX_FRAMES + t] = mel_out[t * AudioProcessor::N_MELS + m];
        }
    }
    TfLiteTensorCopyFromBuffer(voc_in, voc_in_buf.data(), voc_in_buf.size() * sizeof(float));

    if (TfLiteInterpreterInvoke(vocos_interp_) != kTfLiteOk) {
        LOGE("[LiteRTIndicEngine] Vocos invoke failed");
        return {};
    }

    auto t_voc = std::chrono::high_resolution_clock::now();

    // 6. iSTFT Waveform Synthesis
    const TfLiteTensor* voc_out = TfLiteInterpreterGetOutputTensor(vocos_interp_, 0);
    const size_t spec_plane = 513 * AudioProcessor::MAX_FRAMES;
    std::vector<float> spec_data(2 * spec_plane);
    TfLiteTensorCopyToBuffer(voc_out, spec_data.data(), spec_data.size() * sizeof(float));

    const float* spec_real = spec_data.data();
    const float* spec_imag = spec_data.data() + spec_plane;


    std::vector<float> full_waveform = audio_proc_.synthesizeWaveform(spec_real, spec_imag, total_frames);

    // Slice only the generated target audio (skip reference audio frames)
    size_t ref_samples = static_cast<size_t>(ref_frames) * AudioProcessor::HOP_LENGTH;
    std::vector<float> gen_waveform;
    if (full_waveform.size() > ref_samples) {
        gen_waveform.assign(full_waveform.begin() + ref_samples, full_waveform.end());
    } else {
        gen_waveform = std::move(full_waveform);
    }

    auto t_istft = std::chrono::high_resolution_clock::now();

    // 7. Telemetry recording
    if (out_telemetry) {
        out_telemetry->mel_extract_time_ms = std::chrono::duration<float, std::milli>(t_mel - t_start).count();
        out_telemetry->diffusion_time_ms = std::chrono::duration<float, std::milli>(t_diff - t_mel).count();
        out_telemetry->vocos_time_ms = std::chrono::duration<float, std::milli>(t_voc - t_diff).count();
        out_telemetry->istft_time_ms = std::chrono::duration<float, std::milli>(t_istft - t_voc).count();
        out_telemetry->total_time_ms = std::chrono::duration<float, std::milli>(t_istft - t_start).count();
        out_telemetry->audio_duration_sec = static_cast<float>(gen_waveform.size()) / AudioProcessor::SAMPLE_RATE;
        out_telemetry->real_time_factor = (out_telemetry->total_time_ms / 1000.0f) / std::max(out_telemetry->audio_duration_sec, 0.01f);
    }

    return gen_waveform;
}

} // namespace indic
