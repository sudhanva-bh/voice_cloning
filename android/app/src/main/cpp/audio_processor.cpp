#include "audio_processor.h"
#include <cmath>
#include <algorithm>
#include <cstring>
#include <iostream>

namespace indic {

static inline float hzToMel(float hz) {
    return 2595.0f * std::log10(1.0f + hz / 700.0f);
}

static inline float melToHz(float mel) {
    return 700.0f * (std::pow(10.0f, mel / 2595.0f) - 1.0f);
}

AudioProcessor::AudioProcessor() {
    fft_cfg_ = kiss_fftr_alloc(N_FFT, 0, nullptr, nullptr);
    ifft_cfg_ = kiss_fftr_alloc(N_FFT, 1, nullptr, nullptr);
    initHannWindow();
    initMelFilterbank();
}

AudioProcessor::~AudioProcessor() {
    if (fft_cfg_) free(fft_cfg_);
    if (ifft_cfg_) free(ifft_cfg_);
}

void AudioProcessor::initHannWindow() {
    hann_window_.resize(N_FFT);
    for (int i = 0; i < N_FFT; ++i) {
        hann_window_[i] = 0.5f * (1.0f - std::cos(2.0f * M_PI * i / N_FFT));
    }
}

void AudioProcessor::initMelFilterbank() {
    int num_bins = N_FFT / 2 + 1; // 513
    mel_filters_.assign(N_MELS, std::vector<float>(num_bins, 0.0f));

    float min_mel = hzToMel(0.0f);
    float max_mel = hzToMel(SAMPLE_RATE / 2.0f); // 12000 Hz

    std::vector<float> mel_points(N_MELS + 2);
    for (int i = 0; i < N_MELS + 2; ++i) {
        mel_points[i] = min_mel + i * (max_mel - min_mel) / (N_MELS + 1);
    }

    std::vector<int> bin_points(N_MELS + 2);
    for (int i = 0; i < N_MELS + 2; ++i) {
        float hz = melToHz(mel_points[i]);
        bin_points[i] = std::min(num_bins - 1, static_cast<int>(std::floor((N_FFT + 1) * hz / SAMPLE_RATE)));
    }

    for (int m = 1; m <= N_MELS; ++m) {
        int left = bin_points[m - 1];
        int center = bin_points[m];
        int right = bin_points[m + 1];

        for (int k = left; k < center; ++k) {
            if (center != left) {
                mel_filters_[m - 1][k] = static_cast<float>(k - left) / (center - left);
            }
        }
        for (int k = center; k < right; ++k) {
            if (right != center) {
                mel_filters_[m - 1][k] = static_cast<float>(right - k) / (right - center);
            }
        }
    }
}

int AudioProcessor::extractMel(const float* audio_data, size_t num_samples, float* mel_out, int max_frames) {
    if (num_samples < static_cast<size_t>(N_FFT)) {
        return 0;
    }

    int total_frames = static_cast<int>((num_samples - N_FFT) / HOP_LENGTH) + 1;
    int frames = std::min(total_frames, max_frames);

    std::vector<kiss_fft_scalar> frame_in(N_FFT);
    std::vector<kiss_fft_cpx> frame_out(N_FFT / 2 + 1);

    for (int t = 0; t < frames; ++t) {
        size_t offset = t * HOP_LENGTH;
        for (int n = 0; n < N_FFT; ++n) {
            frame_in[n] = audio_data[offset + n] * hann_window_[n];
        }

        kiss_fftr(fft_cfg_, frame_in.data(), frame_out.data());

        // Linear power spectrum
        std::vector<float> power_spec(N_FFT / 2 + 1);
        for (int k = 0; k <= N_FFT / 2; ++k) {
            power_spec[k] = frame_out[k].r * frame_out[k].r + frame_out[k].i * frame_out[k].i;
        }

        // Apply 100 mel filterbanks & log clamp
        for (int m = 0; m < N_MELS; ++m) {
            float energy = 0.0f;
            for (int k = 0; k <= N_FFT / 2; ++k) {
                energy += power_spec[k] * mel_filters_[m][k];
            }
            // Clamp min 1e-5 and log()
            mel_out[t * N_MELS + m] = std::log(std::max(energy, 1e-5f));
        }
    }

    return frames;
}

std::vector<float> AudioProcessor::synthesizeWaveform(const float* spec_real, const float* spec_imag, int num_frames) {
    int num_bins = N_FFT / 2 + 1; // 513
    size_t out_len = static_cast<size_t>(num_frames - 1) * HOP_LENGTH + N_FFT;
    std::vector<float> output_waveform(out_len, 0.0f);
    std::vector<float> window_envelope(out_len, 0.0f);

    std::vector<kiss_fft_cpx> freq_frame(num_bins);
    std::vector<kiss_fft_scalar> time_frame(N_FFT);

    for (int t = 0; t < num_frames; ++t) {
        for (int k = 0; k < num_bins; ++k) {
            // [513, 512] column-major or row-major depending on input
            freq_frame[k].r = spec_real[k * num_frames + t];
            freq_frame[k].i = spec_imag[k * num_frames + t];
        }

        kiss_fftri(ifft_cfg_, freq_frame.data(), time_frame.data());

        size_t offset = static_cast<size_t>(t) * HOP_LENGTH;
        for (int n = 0; n < N_FFT; ++n) {
            float win = hann_window_[n];
            // Normalize kiss_fftri division by N_FFT
            float sample = (time_frame[n] / static_cast<float>(N_FFT)) * win;
            output_waveform[offset + n] += sample;
            window_envelope[offset + n] += win * win;
        }
    }

    // Overlap-add window normalization & peak scaling
    float peak = 0.0f;
    for (size_t i = 0; i < out_len; ++i) {
        if (window_envelope[i] > 1e-4f) {
            output_waveform[i] /= window_envelope[i];
        }
        peak = std::max(peak, std::abs(output_waveform[i]));
    }

    if (peak > 1e-4f) {
        float scale = 0.95f / peak;
        for (size_t i = 0; i < out_len; ++i) {
            output_waveform[i] *= scale;
        }
    }

    return output_waveform;
}

std::vector<float> AudioProcessor::decodeWavBytes(const uint8_t* wav_bytes, size_t byte_len, int* out_sample_rate) {
    std::vector<float> samples;
    if (byte_len < 44) return samples;

    // Verify RIFF header
    if (std::memcmp(wav_bytes, "RIFF", 4) != 0 || std::memcmp(wav_bytes + 8, "WAVE", 4) != 0) {
        return samples;
    }

    // Parse fmt chunk
    size_t pos = 12;
    int channels = 1;
    int sr = 24000;
    int bits_per_sample = 16;
    size_t data_pos = 0;
    size_t data_bytes = 0;

    while (pos + 8 <= byte_len) {
        char chunk_id[5] = {0};
        std::memcpy(chunk_id, wav_bytes + pos, 4);
        uint32_t chunk_size = *reinterpret_cast<const uint32_t*>(wav_bytes + pos + 4);
        pos += 8;

        if (std::strcmp(chunk_id, "fmt ") == 0 && chunk_size >= 16) {
            channels = *reinterpret_cast<const uint16_t*>(wav_bytes + pos + 2);
            sr = *reinterpret_cast<const uint32_t*>(wav_bytes + pos + 4);
            bits_per_sample = *reinterpret_cast<const uint16_t*>(wav_bytes + pos + 14);
        } else if (std::strcmp(chunk_id, "data") == 0) {
            data_pos = pos;
            data_bytes = std::min(static_cast<size_t>(chunk_size), byte_len - pos);
            break;
        }
        pos += chunk_size;
    }

    if (out_sample_rate) *out_sample_rate = sr;
    if (data_pos == 0 || bits_per_sample != 16) return samples;

    size_t num_samples_total = data_bytes / 2;
    size_t num_frames = num_samples_total / channels;
    samples.resize(num_frames);

    const int16_t* pcm16 = reinterpret_cast<const int16_t*>(wav_bytes + data_pos);
    for (size_t i = 0; i < num_frames; ++i) {
        float val = 0.0f;
        for (int ch = 0; ch < channels; ++ch) {
            val += static_cast<float>(pcm16[i * channels + ch]) / 32768.0f;
        }
        samples[i] = val / channels;
    }

    return samples;
}

} // namespace indic
