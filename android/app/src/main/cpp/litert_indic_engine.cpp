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

    TfLiteXNNPackDelegateOptions dit_xnnpack_opts = TfLiteXNNPackDelegateOptionsDefault();
    dit_xnnpack_opts.num_threads = num_threads_;
    dit_xnnpack_delegate_ = TfLiteXNNPackDelegateCreate(&dit_xnnpack_opts);
    if (dit_xnnpack_delegate_) {
        TfLiteInterpreterOptionsAddDelegate(dit_options, dit_xnnpack_delegate_);
        LOGI("[LiteRTIndicEngine] Attached official XNNPACK delegate to DiT interpreter options (%d threads)", num_threads_);
    }

    dit_interp_ = TfLiteInterpreterCreate(dit_model_, dit_options);
    TfLiteInterpreterOptionsDelete(dit_options);

    if (!dit_interp_) {
        LOGE("[LiteRTIndicEngine] Failed to create DiT interpreter from file");
        return false;
    }

    TfLiteStatus alloc_status = TfLiteInterpreterAllocateTensors(dit_interp_);
    if (alloc_status != kTfLiteOk) {
        LOGE("[LiteRTIndicEngine] Failed to allocate DiT tensors from file (status=%d)", alloc_status);
        return false;
    }
    LOGI("[LiteRTIndicEngine] DiT tensors allocated successfully with XNNPACK");

    // 3. Initialize Vocos Interpreter from file
    vocos_model_ = TfLiteModelCreateFromFile(vocos_model_path.c_str());
    if (!vocos_model_) {
        LOGE("[LiteRTIndicEngine] Failed to create Vocos model from file: %s", vocos_model_path.c_str());
        return false;
    }

    TfLiteInterpreterOptions* vocos_options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreterOptionsSetNumThreads(vocos_options, num_threads_);

    TfLiteXNNPackDelegateOptions vocos_xnnpack_opts = TfLiteXNNPackDelegateOptionsDefault();
    vocos_xnnpack_opts.num_threads = num_threads_;
    vocos_xnnpack_delegate_ = TfLiteXNNPackDelegateCreate(&vocos_xnnpack_opts);
    if (vocos_xnnpack_delegate_) {
        TfLiteInterpreterOptionsAddDelegate(vocos_options, vocos_xnnpack_delegate_);
        LOGI("[LiteRTIndicEngine] Attached official XNNPACK delegate to Vocos interpreter options (%d threads)", num_threads_);
    }

    vocos_interp_ = TfLiteInterpreterCreate(vocos_model_, vocos_options);
    TfLiteInterpreterOptionsDelete(vocos_options);

    if (!vocos_interp_) {
        LOGE("[LiteRTIndicEngine] Failed to create Vocos interpreter from file");
        return false;
    }

    if (TfLiteInterpreterAllocateTensors(vocos_interp_) != kTfLiteOk) {
        LOGE("[LiteRTIndicEngine] Failed to allocate Vocos tensors from file");
        return false;
    }
    LOGI("[LiteRTIndicEngine] Vocos tensors allocated successfully with XNNPACK");

    ready_ = true;
    return true;
}


bool LiteRTIndicEngine::setReferenceAudio(
    const float* ref_pcm, size_t ref_pcm_samples,
    const std::string& ref_text
) {
    if (!ready_ || !ref_pcm || ref_pcm_samples == 0) {
        LOGE("[LiteRTIndicEngine] setReferenceAudio: Engine not ready or invalid PCM");
        return false;
    }

    cached_ref_mel_.assign(AudioProcessor::MAX_FRAMES * AudioProcessor::N_MELS, 0.0f);
    cached_ref_frames_ = audio_proc_.extractMel(ref_pcm, ref_pcm_samples, cached_ref_mel_.data(), AudioProcessor::MAX_FRAMES);
    cached_ref_text_ = ref_text;
    has_cached_ref_ = (cached_ref_frames_ > 0);

    LOGI("[LiteRTIndicEngine] Cached reference audio: frames=%d, text_len=%zu", cached_ref_frames_, cached_ref_text_.length());
    return has_cached_ref_;
}

std::vector<float> LiteRTIndicEngine::synthesizeChunk(
    const std::string& chunk_text,
    int num_steps,
    float cfg_strength,
    uint32_t seed,
    EngineTelemetry* out_telemetry
) {
    if (!ready_ || !has_cached_ref_) {
        LOGE("[LiteRTIndicEngine] synthesizeChunk: Engine not ready or no reference audio cached");
        return {};
    }

    auto t_start = std::chrono::high_resolution_clock::now();

    // 1. Duration allocation using cached reference frames
    size_t ref_char_len = std::max<size_t>(cached_ref_text_.length(), 1);
    size_t gen_char_len = std::max<size_t>(chunk_text.length(), 1);
    int gen_frames = static_cast<int>(static_cast<float>(cached_ref_frames_) / ref_char_len * gen_char_len * 1.05f);

    // Enforce a minimum frame floor of 80 frames (~0.85s) for short / single-word utterances.
    // This provides the necessary acoustic headroom for the DiT inter-utterance transition
    // pause, consonant attack, and phoneme articulation before any slicing occurs.
    gen_frames = std::max(gen_frames, 80);

    int total_frames = std::min(cached_ref_frames_ + gen_frames, AudioProcessor::MAX_FRAMES);
    gen_frames = total_frames - cached_ref_frames_;

    // 2. Prepare conditioning mel and tokens
    std::vector<float> cond_mel(EulerSampler::LATENT_ELEMENTS, 0.0f);
    std::memcpy(cond_mel.data(), cached_ref_mel_.data(), cached_ref_frames_ * AudioProcessor::N_MELS * sizeof(float));

    // Ensure utterance has clean terminal punctuation so DiT tokenizers recognize completion
    std::string sanitized_chunk = chunk_text;
    if (!sanitized_chunk.empty()) {
        char last = sanitized_chunk.back();
        if (last != '.' && last != '!' && last != '?' && last != ',' && last != ';') {
            sanitized_chunk += ".";
        }
    }

    std::string full_text = cached_ref_text_ + " " + sanitized_chunk;
    std::vector<int32_t> text_tokens = tokenizer_.encode(full_text, EulerSampler::TEXT_LEN, -1);

    auto t_mel = std::chrono::high_resolution_clock::now();

    // 3. Run CFM Euler ODE Sampler
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
        LOGE("EulerSampler failed to complete CFM ODE steps in chunk");
        return {};
    }

    auto t_diff = std::chrono::high_resolution_clock::now();

    // 4. Vocos Neural Vocoding
    std::memcpy(mel_out.data(), cached_ref_mel_.data(), cached_ref_frames_ * AudioProcessor::N_MELS * sizeof(float));

    // Transpose mel from [512, 100] (time, mel) to Vocos input layout [1, 100, 512] (mel, time)
    TfLiteTensor* voc_in = TfLiteInterpreterGetInputTensor(vocos_interp_, 0);
    std::vector<float> voc_in_buf(AudioProcessor::N_MELS * AudioProcessor::MAX_FRAMES);

    for (int t = 0; t < AudioProcessor::MAX_FRAMES; ++t) {
        for (int m = 0; m < AudioProcessor::N_MELS; ++m) {
            voc_in_buf[m * AudioProcessor::MAX_FRAMES + t] = mel_out[t * AudioProcessor::N_MELS + m];
        }
    }
    TfLiteTensorCopyFromBuffer(voc_in, voc_in_buf.data(), voc_in_buf.size() * sizeof(float));

    if (TfLiteInterpreterInvoke(vocos_interp_) != kTfLiteOk) {
        LOGE("[LiteRTIndicEngine] Vocos invoke failed in chunk");
        return {};
    }

    auto t_voc = std::chrono::high_resolution_clock::now();

    // 5. iSTFT Waveform Synthesis
    const TfLiteTensor* voc_out = TfLiteInterpreterGetOutputTensor(vocos_interp_, 0);
    const size_t spec_plane = 513 * AudioProcessor::MAX_FRAMES;
    std::vector<float> spec_data(2 * spec_plane);
    TfLiteTensorCopyToBuffer(voc_out, spec_data.data(), spec_data.size() * sizeof(float));

    const float* spec_real = spec_data.data();
    const float* spec_imag = spec_data.data() + spec_plane;

    std::vector<float> full_waveform = audio_proc_.synthesizeWaveform(spec_real, spec_imag, AudioProcessor::MAX_FRAMES);

    // Slice only the generated target audio (skip reference audio frames, end at total_frames)
    size_t ref_samples = static_cast<size_t>(cached_ref_frames_) * AudioProcessor::HOP_LENGTH;
    size_t end_samples = std::min(static_cast<size_t>(total_frames) * AudioProcessor::HOP_LENGTH, full_waveform.size());
    std::vector<float> gen_waveform;
    if (full_waveform.size() > ref_samples) {
        gen_waveform.assign(full_waveform.begin() + ref_samples, full_waveform.begin() + end_samples);
    } else {
        gen_waveform = std::move(full_waveform);
    }

    // Target audio peak normalization: only amplify if audible speech is present (peak >= 0.03f)
    // Prevents amplifying sub-audible background noise/static by 500x
    float peak = 0.0f;
    for (float s : gen_waveform) {
        if (std::abs(s) > peak) peak = std::abs(s);
    }
    if (peak >= 0.03f) {
        float scale = 0.95f / peak;
        for (float& s : gen_waveform) {
            s *= scale;
        }
    }

    auto t_istft = std::chrono::high_resolution_clock::now();

    // 6. Telemetry recording
    if (out_telemetry) {
        out_telemetry->mel_extract_time_ms = 0.0f; // Precomputed & cached!
        out_telemetry->diffusion_time_ms = std::chrono::duration<float, std::milli>(t_diff - t_mel).count();
        out_telemetry->vocos_time_ms = std::chrono::duration<float, std::milli>(t_voc - t_diff).count();
        out_telemetry->istft_time_ms = std::chrono::duration<float, std::milli>(t_istft - t_voc).count();
        out_telemetry->total_time_ms = std::chrono::duration<float, std::milli>(t_istft - t_start).count();
        out_telemetry->audio_duration_sec = static_cast<float>(gen_waveform.size()) / AudioProcessor::SAMPLE_RATE;
        out_telemetry->real_time_factor = (out_telemetry->total_time_ms / 1000.0f) / std::max(out_telemetry->audio_duration_sec, 0.01f);
    }

    return gen_waveform;
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

    if (!setReferenceAudio(ref_pcm, ref_pcm_samples, ref_text)) {
        LOGE("[LiteRTIndicEngine] synthesize: Failed to set reference audio");
        return {};
    }

    auto t_mel = std::chrono::high_resolution_clock::now();

    std::vector<float> result = synthesizeChunk(target_text, num_steps, cfg_strength, seed, out_telemetry);

    if (out_telemetry) {
        out_telemetry->mel_extract_time_ms = std::chrono::duration<float, std::milli>(t_mel - t_start).count();
        out_telemetry->total_time_ms += out_telemetry->mel_extract_time_ms;
        out_telemetry->real_time_factor = (out_telemetry->total_time_ms / 1000.0f) / std::max(out_telemetry->audio_duration_sec, 0.01f);
    }

    return result;
}

} // namespace indic
