#ifndef LITERT_INDIC_ENGINE_H
#define LITERT_INDIC_ENGINE_H

#include <string>
#include <vector>
#include <memory>
#include "tensorflow/lite/c/c_api.h"
#include "tensorflow/lite/delegates/xnnpack/xnnpack_delegate.h"
#include "indic_tokenizer.h"
#include "audio_processor.h"
#include "euler_sampler.h"

namespace indic {

struct EngineTelemetry {
    float mel_extract_time_ms;
    float diffusion_time_ms;
    float vocos_time_ms;
    float istft_time_ms;
    float total_time_ms;
    float audio_duration_sec;
    float real_time_factor;
};

class LiteRTIndicEngine {
public:
    LiteRTIndicEngine();
    ~LiteRTIndicEngine();

    // Initialize engine with memory-mapped FlatBuffers from APK assets
    bool initialize(
        const void* dit_model_data, size_t dit_model_size,
        const void* vocos_model_data, size_t vocos_model_size,
        const char* vocab_data, size_t vocab_size,
        int num_threads = 5
    );

    // Initialize engine directly from file paths on local storage
    bool initializeFromFiles(
        const std::string& dit_model_path,
        const std::string& vocos_model_path,
        const std::string& vocab_path,
        int num_threads = 5
    );

    // Set and cache speaker reference audio features for sequential chunk synthesis
    bool setReferenceAudio(
        const float* ref_pcm, size_t ref_pcm_samples,
        const std::string& ref_text
    );

    // Synthesize an individual speech chunk against cached reference audio
    std::vector<float> synthesizeChunk(
        const std::string& chunk_text,
        int num_steps = 8,
        float cfg_strength = 2.0f,
        uint32_t seed = 42,
        EngineTelemetry* out_telemetry = nullptr
    );

    // End-to-end voice cloning synthesis (backward-compatible single-shot)
    std::vector<float> synthesize(
        const float* ref_pcm, size_t ref_pcm_samples,
        const std::string& ref_text,
        const std::string& target_text,
        int num_steps = 8,
        float cfg_strength = 2.0f,
        uint32_t seed = 42,
        EngineTelemetry* out_telemetry = nullptr
    );

    bool isReady() const { return ready_; }
    bool hasReferenceAudio() const { return has_cached_ref_; }

private:
    bool ready_ = false;
    int num_threads_ = 5;

    // Cached speaker conditioning state for multi-chunk synthesis
    bool has_cached_ref_ = false;
    std::vector<float> cached_ref_mel_;
    int cached_ref_frames_ = 0;
    std::string cached_ref_text_;

    TfLiteModel* dit_model_ = nullptr;
    TfLiteInterpreter* dit_interp_ = nullptr;
    TfLiteDelegate* dit_xnnpack_delegate_ = nullptr;

    TfLiteModel* vocos_model_ = nullptr;
    TfLiteInterpreter* vocos_interp_ = nullptr;
    TfLiteDelegate* vocos_xnnpack_delegate_ = nullptr;

    IndicTokenizer tokenizer_;

    AudioProcessor audio_proc_;
    EulerSampler euler_sampler_;
};

} // namespace indic

#endif // LITERT_INDIC_ENGINE_H
