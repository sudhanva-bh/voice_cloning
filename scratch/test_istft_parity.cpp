#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include "kiss_fftr.h"

int main() {
    const int N_FFT = 1024;
    const int HOP_LENGTH = 256;
    const int num_bins = N_FFT / 2 + 1; // 513
    const int num_frames = 10;

    kiss_fftr_cfg cfg_f = kiss_fftr_alloc(N_FFT, 0, nullptr, nullptr);
    kiss_fftr_cfg cfg_i = kiss_fftr_alloc(N_FFT, 1, nullptr, nullptr);

    // Create a simple 440 Hz sine wave
    std::vector<float> orig_signal((num_frames - 1) * HOP_LENGTH + N_FFT, 0.0f);
    for (size_t i = 0; i < orig_signal.size(); ++i) {
        orig_signal[i] = std::sin(2.0f * M_PI * 440.0f * i / 24000.0f);
    }

    std::vector<float> hann(N_FFT);
    for (int i = 0; i < N_FFT; ++i) {
        hann[i] = 0.5f * (1.0f - std::cos(2.0f * M_PI * i / N_FFT));
    }

    // STFT
    std::vector<std::vector<kiss_fft_cpx>> spec(num_frames, std::vector<kiss_fft_cpx>(num_bins));
    for (int t = 0; t < num_frames; ++t) {
        std::vector<float> frame_in(N_FFT);
        for (int n = 0; n < N_FFT; ++n) {
            frame_in[n] = orig_signal[t * HOP_LENGTH + n] * hann[n];
        }
        kiss_fftr(cfg_f, frame_in.data(), spec[t].data());
    }

    // iSTFT with overlap-add
    size_t out_len = (num_frames - 1) * HOP_LENGTH + N_FFT;
    std::vector<float> out_wav(out_len, 0.0f);
    std::vector<float> out_env(out_len, 0.0f);

    for (int t = 0; t < num_frames; ++t) {
        std::vector<float> time_frame(N_FFT);
        kiss_fftri(cfg_i, spec[t].data(), time_frame.data());
        size_t offset = t * HOP_LENGTH;
        for (int n = 0; n < N_FFT; ++n) {
            float win = hann[n];
            float s = (time_frame[n] / static_cast<float>(N_FFT)) * win;
            out_wav[offset + n] += s;
            out_env[offset + n] += win * win;
        }
    }

    for (size_t i = 0; i < out_len; ++i) {
        if (out_env[i] > 1e-4f) {
            out_wav[i] /= out_env[i];
        }
    }

    // Check error in the valid overlap region (from N_FFT to out_len - N_FFT)
    float max_err = 0.0f;
    for (size_t i = N_FFT; i < out_len - N_FFT; ++i) {
        float err = std::abs(out_wav[i] - orig_signal[i]);
        if (err > max_err) max_err = err;
    }

    std::cout << "iSTFT overlap-add reconstruction max error: " << max_err << std::endl;
    return 0;
}
