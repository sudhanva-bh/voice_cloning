#ifndef EULER_SAMPLER_H
#define EULER_SAMPLER_H

#include <vector>
#include <cstdint>
#include <random>
#include "tensorflow/lite/c/c_api.h"

namespace indic {

class EulerSampler {
public:
    static constexpr int FRAMES = 512;
    static constexpr int MEL_BINS = 100;
    static constexpr int TEXT_LEN = 128;
    static constexpr size_t LATENT_ELEMENTS = FRAMES * MEL_BINS; // 51,200 floats

    EulerSampler() = default;

    // Run CFM Euler ODE sampling loop using the LiteRT DiT interpreter
    // Output: mel_generated buffer of size [FRAMES * MEL_BINS]
    bool sample(
        TfLiteInterpreter* dit_interp,
        const float* cond_mel,        // [FRAMES, MEL_BINS]
        const int32_t* text_tokens,   // [TEXT_LEN]
        float* mel_out,               // [FRAMES, MEL_BINS]
        int num_steps = 16,
        float cfg_strength = 2.0f,
        float sway_coef = -1.0f,
        uint32_t seed = 42
    );

private:
    std::vector<float> computeSwaySchedule(int num_steps, float sway_coef) const;
};

} // namespace indic

#endif // EULER_SAMPLER_H
