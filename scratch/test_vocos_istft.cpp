#include <iostream>
#include <fstream>
#include <vector>
#include "audio_processor.h"

int main() {
    // Read spec_real and spec_imag exported from python Vocos
    std::ifstream f("/mnt/c/voice_cloning/scratch/debug_vocos_spec.bin", std::ios::binary);
    if (!f.is_open()) {
        std::cerr << "Failed to open debug_vocos_spec.bin" << std::endl;
        return 1;
    }
    const int MAX_FRAMES = 512;
    const int NUM_BINS = 513;
    size_t plane = NUM_BINS * MAX_FRAMES;
    std::vector<float> spec_data(2 * plane);
    f.read(reinterpret_cast<char*>(spec_data.data()), spec_data.size() * sizeof(float));

    const float* spec_real = spec_data.data();
    const float* spec_imag = spec_data.data() + plane;

    indic::AudioProcessor proc;
    std::vector<float> full_wav = proc.synthesizeWaveform(spec_real, spec_imag, MAX_FRAMES);

    std::cout << "Synthesized samples: " << full_wav.size() << std::endl;

    std::ofstream out("/mnt/c/voice_cloning/scratch/debug_cpp_synth.bin", std::ios::binary);
    out.write(reinterpret_cast<const char*>(full_wav.data()), full_wav.size() * sizeof(float));
    std::cout << "Saved debug_cpp_synth.bin" << std::endl;
    return 0;
}
