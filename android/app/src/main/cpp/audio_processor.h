#ifndef AUDIO_PROCESSOR_H
#define AUDIO_PROCESSOR_H

#include <vector>
#include <cstdint>
#include <cstddef>
#include "kissfft/kiss_fftr.h"

namespace indic {

class AudioProcessor {
public:
    static constexpr int SAMPLE_RATE = 24000;
    static constexpr int N_FFT = 1024;
    static constexpr int HOP_LENGTH = 256;
    static constexpr int N_MELS = 100;
    static constexpr int MAX_FRAMES = 512;

    AudioProcessor();
    ~AudioProcessor();

    // Extract 100-mel log spectrogram from 24 kHz float PCM audio
    // Output: mel_out buffer of shape [T, N_MELS], where T is returned frame count
    int extractMel(const float* audio_data, size_t num_samples, float* mel_out, int max_frames = MAX_FRAMES);

    // Reconstruct audio from Vocos complex spectrogram
    // spec_real and spec_imag are 513 x num_frames matrices
    // Returns synthesized 24 kHz float PCM samples
    std::vector<float> synthesizeWaveform(const float* spec_real, const float* spec_imag, int num_frames);

    // Parse 16-bit PCM WAV byte buffer into float array
    static std::vector<float> decodeWavBytes(const uint8_t* wav_bytes, size_t byte_len, int* out_sample_rate = nullptr);

private:
    void initHannWindow();

    kiss_fftr_cfg fft_cfg_;
    kiss_fftr_cfg ifft_cfg_;
    std::vector<float> hann_window_;
};

} // namespace indic

#endif // AUDIO_PROCESSOR_H
