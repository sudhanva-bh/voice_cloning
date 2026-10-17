#include "audio_processor.h"
#include "mel_filterbank.h"
#include <cmath>
#include <algorithm>
#include <cstring>
#include <iostream>

namespace indic {

AudioProcessor::AudioProcessor() {
    fft_cfg_ = kiss_fftr_alloc(N_FFT, 0, nullptr, nullptr);
    ifft_cfg_ = kiss_fftr_alloc(N_FFT, 1, nullptr, nullptr);
    initHannWindow();
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

int AudioProcessor::extractMel(const float* audio_data, size_t num_samples, float* mel_out, int max_frames) {
    if (num_samples == 0) {
        return 0;
    }

    // 1. RMS normalization to target_rms = 0.1 (matches torchaudio & F5-TTS)
    float sum_sq = 0.0f;
    for (size_t i = 0; i < num_samples; ++i) {
        sum_sq += audio_data[i] * audio_data[i];
    }
    float rms = std::sqrt(sum_sq / static_cast<float>(num_samples));
    float scale = 1.0f;
    if (rms < 0.1f && rms > 1e-6f) {
        scale = 0.1f / rms;
    }

    // 2. Center padding with N_FFT / 2 (512 samples) on both sides (torchaudio center=True)
    size_t pad = N_FFT / 2; // 512
    size_t padded_len = num_samples + 2 * pad;
    std::vector<float> padded_audio(padded_len, 0.0f);
    for (size_t i = 0; i < num_samples; ++i) {
        padded_audio[pad + i] = audio_data[i] * scale;
    }
    // Reflection padding
    for (size_t i = 0; i < pad; ++i) {
        size_t src = (i < num_samples) ? pad + (pad - i) : pad;
        if (src >= padded_len) src = pad;
        padded_audio[i] = padded_audio[src];
    }
    for (size_t i = 0; i < pad; ++i) {
        size_t src = (num_samples > 1 + i) ? pad + num_samples - 2 - i : pad + num_samples - 1;
        if (src >= padded_len) src = pad + num_samples - 1;
        padded_audio[pad + num_samples + i] = padded_audio[src];
    }

    int total_frames = static_cast<int>(num_samples / HOP_LENGTH) + 1;
    int frames = std::min(total_frames, max_frames);

    std::vector<kiss_fft_scalar> frame_in(N_FFT);
    std::vector<kiss_fft_cpx> frame_out(N_FFT / 2 + 1);
    std::vector<float> mag_spec(N_FFT / 2 + 1);

    for (int t = 0; t < frames; ++t) {
        size_t offset = static_cast<size_t>(t) * HOP_LENGTH;
        for (int n = 0; n < N_FFT; ++n) {
            frame_in[n] = padded_audio[offset + n] * hann_window_[n];
        }

        kiss_fftr(fft_cfg_, frame_in.data(), frame_out.data());

        // Magnitude spectrum (power = 1)
        for (int k = 0; k <= N_FFT / 2; ++k) {
            mag_spec[k] = std::sqrt(frame_out[k].r * frame_out[k].r + frame_out[k].i * frame_out[k].i);
        }

        // Apply 100 mel filterbanks (TORCHAUDIO_MEL_FB is [513][100]) & clamp min 1e-5, log()
        for (int m = 0; m < N_MELS; ++m) {
            float energy = 0.0f;
            for (int k = 0; k <= N_FFT / 2; ++k) {
                energy += mag_spec[k] * TORCHAUDIO_MEL_FB[k][m];
            }
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
            // Vocos output is [1, 2, 513, 512] row-major in time (stride = MAX_FRAMES = 512)
            freq_frame[k].r = spec_real[k * MAX_FRAMES + t];
            freq_frame[k].i = spec_imag[k * MAX_FRAMES + t];
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

    // Overlap-add window normalization
    for (size_t i = 0; i < out_len; ++i) {
        if (window_envelope[i] > 1e-4f) {
            output_waveform[i] /= window_envelope[i];
        }
    }

    // Strip padding: PyTorch istft(center=True) strips N_FFT / 2 (512) from front and back
    size_t pad = N_FFT / 2; // 512
    if (out_len <= 2 * pad) {
        return {};
    }
    size_t trimmed_len = out_len - 2 * pad;
    std::vector<float> trimmed_waveform(output_waveform.begin() + pad, output_waveform.begin() + pad + trimmed_len);

    // Peak normalization
    float peak = 0.0f;
    for (float s : trimmed_waveform) {
        peak = std::max(peak, std::abs(s));
    }

    if (peak > 1e-4f) {
        float scale = 0.95f / peak;
        for (float& s : trimmed_waveform) {
            s *= scale;
        }
    }

    return trimmed_waveform;
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
