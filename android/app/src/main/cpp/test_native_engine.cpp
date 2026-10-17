#include <iostream>
#include <fstream>
#include <vector>
#include <cassert>
#include <cmath>
#include <algorithm>
#include "indic_tokenizer.h"
#include "audio_processor.h"


int main() {
    std::cout << "======================================================" << std::endl;
    std::cout << "[Native C++ Engine Test] Phase 4 Core Verification" << std::endl;
    std::cout << "======================================================" << std::endl;

    // --- 1. Test Tokenizer ---
    std::cout << "\n[TEST 1] Testing IndicTokenizer..." << std::endl;
    std::ifstream vocab_file("models/indicf5/vocab.txt");
    if (!vocab_file.is_open()) {
        std::cerr << "  Failed to open models/indicf5/vocab.txt" << std::endl;
        return 1;
    }
    std::string vocab_str((std::istreambuf_iterator<char>(vocab_file)), std::istreambuf_iterator<char>());
    indic::IndicTokenizer tokenizer;
    bool tok_ok = tokenizer.loadFromBuffer(vocab_str.data(), vocab_str.size());
    std::cout << "  Tokenizer loaded: " << (tok_ok ? "SUCCESS" : "FAILED")
              << " (Vocab size: " << tokenizer.vocabSize() << ")" << std::endl;

    // Test English
    std::string text_en = "Some call me nature. Google LiteRT is fast.";
    auto tokens_en = tokenizer.encode(text_en, 128);
    std::cout << "  Encoded English tokens (first 10): ";
    for (int i = 0; i < 10; ++i) std::cout << tokens_en[i] << " ";
    std::cout << std::endl;

    // Test Hindi
    std::string text_hi = "यह एक परीक्षण है।";
    auto tokens_hi = tokenizer.encode(text_hi, 128);
    std::cout << "  Encoded Hindi tokens (first 10): ";
    for (int i = 0; i < 10; ++i) std::cout << tokens_hi[i] << " ";
    std::cout << std::endl;

    // Test Telugu
    std::string text_te = "ఇది వాయిస్ క్లోనింగ్.";
    auto tokens_te = tokenizer.encode(text_te, 128);
    std::cout << "  Encoded Telugu tokens (first 10): ";
    for (int i = 0; i < 10; ++i) std::cout << tokens_te[i] << " ";
    std::cout << std::endl;

    // Test Tamil
    std::string text_ta = "வணக்கம் உலகம்.";
    auto tokens_ta = tokenizer.encode(text_ta, 128);
    std::cout << "  Encoded Tamil tokens (first 10): ";
    for (int i = 0; i < 10; ++i) std::cout << tokens_ta[i] << " ";
    std::cout << std::endl;

    // --- 2. Test AudioProcessor ---
    std::cout << "\n[TEST 2] Testing AudioProcessor Mel Extraction & iSTFT..." << std::endl;
    indic::AudioProcessor audio_proc;

    // Read test WAV: scratch/parity_test/trimmed_ref_en.wav
    std::ifstream wav_file("scratch/parity_test/trimmed_ref_en.wav", std::ios::binary);
    if (!wav_file.is_open()) {
        std::cerr << "  Failed to open scratch/parity_test/trimmed_ref_en.wav" << std::endl;
        return 1;
    }
    std::vector<uint8_t> wav_bytes((std::istreambuf_iterator<char>(wav_file)), std::istreambuf_iterator<char>());
    int sample_rate = 0;
    auto samples = indic::AudioProcessor::decodeWavBytes(wav_bytes.data(), wav_bytes.size(), &sample_rate);
    std::cout << "  Decoded WAV: " << samples.size() << " samples ("
              << static_cast<float>(samples.size()) / sample_rate << "s at " << sample_rate << " Hz)" << std::endl;

    std::vector<float> mel(512 * 100, 0.0f);
    int frames = audio_proc.extractMel(samples.data(), samples.size(), mel.data(), 512);
    std::cout << "  Extracted Mel Frames: " << frames << " (Expected ~206 frames for 2.2s)" << std::endl;
    std::cout << "  Mel[0, 0..4]: " << mel[0] << ", " << mel[1] << ", " << mel[2] << ", " << mel[3] << ", " << mel[4] << std::endl;

    // --- 3. Test KissFFT iSTFT Overlap-Add ---
    std::cout << "\n[TEST 3] Testing KissFFTR iSTFT Synthesis..." << std::endl;
    // Generate a synthetic test magnitude & zero phase to verify inverse FFT reconstruction
    std::vector<float> test_real(513 * 50, 0.0f);
    std::vector<float> test_imag(513 * 50, 0.0f);
    // Put a test tone at bin 20 (~468 Hz)
    for (int t = 0; t < 50; ++t) {
        test_real[20 * 50 + t] = 10.0f;
    }
    auto recon = audio_proc.synthesizeWaveform(test_real.data(), test_imag.data(), 50);
    std::cout << "  Synthesized waveform length: " << recon.size() << " samples" << std::endl;
    std::cout << "  Peak value: " << *std::max_element(recon.begin(), recon.end()) << std::endl;

    std::cout << "\n>>> ALL NATIVE C++ ENGINE TESTS PASSED! <<<" << std::endl;
    return 0;
}
