#include "litert_indic_engine.h"
#include <chrono>
#include <iostream>
#include <cmath>
#include <cstring>

namespace indic {

LiteRTIndicEngine::LiteRTIndicEngine() = default;

LiteRTIndicEngine::~LiteRTIndicEngine() {
    if (dit_interp_) TfLiteInterpreterDelete(dit_interp_);
    if (dit_model_) TfLiteModelDelete(dit_model_);
    if (dit_xnnpack_) TfLiteXNNPackDelegateDelete(dit_xnnpack_);

    if (vocos_interp_) TfLiteInterpreterDelete(vocos_interp_);
    if (vocos_model_) TfLiteModelDelete(vocos_model_);
    if (vocos_xnnpack_) TfLiteXNNPackDelegateDelete(vocos_xnnpack_);
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

    // 2. Initialize DiT Interpreter with XNNPACK
    dit_model_ = TfLiteModelCreate(dit_model_data, dit_model_size);
    if (!dit_model_) {
        std::cerr << "[LiteRTIndicEngine] Failed to create DiT model" << std::endl;
        return false;
    }

    TfLiteInterpreterOptions* dit_options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreterOptionsSetNumThreads(dit_options, num_threads_);

    TfLiteXNNPackDelegateOptions xnnpack_opts = TfLiteXNNPackDelegateOptionsDefault();
    xnnpack_opts.num_threads = num_threads_;
    dit_xnnpack_ = TfLiteXNNPackDelegateCreate(&xnnpack_opts);
    if (dit_xnnpack_) {
        TfLiteInterpreterOptionsAddDelegate(dit_options, dit_xnnpack_);
    }

    dit_interp_ = TfLiteInterpreterCreate(dit_model_, dit_options);
    TfLiteInterpreterOptionsDelete(dit_options);

    if (!dit_interp_ || TfLiteInterpreterAllocateTensors(dit_interp_) != kTfLiteOk) {
        std::cerr << "[LiteRTIndicEngine] Failed to allocate DiT tensors" << std::endl;
        return false;
    }

    // 3. Initialize Vocos Interpreter with XNNPACK
    vocos_model_ = TfLiteModelCreate(vocos_model_data, vocos_model_size);
    if (!vocos_model_) {
        std::cerr << "[LiteRTIndicEngine] Failed to create Vocos model" << std::endl;
        return false;
    }

    TfLiteInterpreterOptions* vocos_options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreterOptionsSetNumThreads(vocos_options, num_threads_);

    vocos_xnnpack_ = TfLiteXNNPackDelegateCreate(&xnnpack_opts);
    if (vocos_xnnpack_) {
        TfLiteInterpreterOptionsAddDelegate(vocos_options, vocos_xnnpack_);
    }

    vocos_interp_ = TfLiteInterpreterCreate(vocos_model_, vocos_options);
    TfLiteInterpreterOptionsDelete(vocos_options);

    if (!vocos_interp_ || TfLiteInterpreterAllocateTensors(vocos_interp_) != kTfLiteOk) {
        std::cerr << "[LiteRTIndicEngine] Failed to allocate Vocos tensors" << std::endl;
        return false;
    }

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
    euler_sampler_.sample(
        dit_interp_,
        cond_mel.data(),
        text_tokens.data(),
        mel_out.data(),
        num_steps,
        cfg_strength,
        -1.0f, // sway_coef
        seed
    );

    auto t_diff = std::chrono::high_resolution_clock::now();

    // 5. Vocos Neural Vocoding
    // Invert conditioning portion: replace generated ref_frames with ground-truth ref_mel
    std::memcpy(mel_out.data(), ref_mel.data(), ref_frames * AudioProcessor::N_MELS * sizeof(float));

    // Transpose mel from [512, 100] (time, mel) to Vocos input layout [1, 100, 512] (mel, time)
    TfLiteTensor* voc_in = TfLiteInterpreterGetInputTensor(vocos_interp_, 0);
    float* voc_in_data = reinterpret_cast<float*>(TfLiteTensorData(voc_in));

    for (int t = 0; t < AudioProcessor::MAX_FRAMES; ++t) {
        for (int m = 0; m < AudioProcessor::N_MELS; ++m) {
            voc_in_data[m * AudioProcessor::MAX_FRAMES + t] = mel_out[t * AudioProcessor::N_MELS + m];
        }
    }

    if (TfLiteInterpreterInvoke(vocos_interp_) != kTfLiteOk) {
        std::cerr << "[LiteRTIndicEngine] Vocos invoke failed" << std::endl;
        return {};
    }

    auto t_voc = std::chrono::high_resolution_clock::now();

    // 6. iSTFT Waveform Synthesis
    const TfLiteTensor* voc_out = TfLiteInterpreterGetOutputTensor(vocos_interp_, 0);
    const float* spec_data = reinterpret_cast<const float*>(TfLiteTensorData(voc_out));

    // Output shape: [1, 2, 513, 512] -> real: [513, 512], imag: [513, 512]
    const size_t spec_plane = 513 * AudioProcessor::MAX_FRAMES;
    const float* spec_real = spec_data;
    const float* spec_imag = spec_data + spec_plane;

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
