#include <iostream>
#include <fstream>
#include <vector>
#include "audio_processor.h"

int main() {
    std::ifstream f("/mnt/c/voice_cloning/scratch/parity_test/trimmed_ref_en.wav", std::ios::binary);
    std::vector<uint8_t> wav_bytes((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    int sr = 24000;
    std::vector<float> pcm = indic::AudioProcessor::decodeWavBytes(wav_bytes.data(), wav_bytes.size(), &sr);
    std::cout << "PCM samples: " << pcm.size() << ", sr: " << sr << std::endl;

    indic::AudioProcessor proc;
    std::vector<float> mel(indic::AudioProcessor::MAX_FRAMES * indic::AudioProcessor::N_MELS, 0.0f);
    int frames = proc.extractMel(pcm.data(), pcm.size(), mel.data(), indic::AudioProcessor::MAX_FRAMES);

    std::cout << "Extracted frames: " << frames << std::endl;
    std::cout << "C++ ref_mel[t=0, m=0..4]: ";
    for (int m = 0; m < 5; ++m) std::cout << mel[0 * indic::AudioProcessor::N_MELS + m] << " ";
    std::cout << std::endl;

    std::cout << "C++ ref_mel[t=1, m=0..4]: ";
    for (int m = 0; m < 5; ++m) std::cout << mel[1 * indic::AudioProcessor::N_MELS + m] << " ";
    std::cout << std::endl;

    float pmin = 1e9f, pmax = -1e9f, psum = 0.0f;
    for (int i = 0; i < frames * 100; ++i) {
        float v = mel[i];
        if (v < pmin) pmin = v;
        if (v > pmax) pmax = v;
        psum += v;
    }
    std::cout << "C++ min: " << pmin << ", max: " << pmax << ", mean: " << psum / (frames * 100) << std::endl;
    return 0;
}
