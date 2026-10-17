#include <iostream>
#include <fstream>
#include "indic_tokenizer.h"

int main() {
    indic::IndicTokenizer tok;
    std::ifstream f("/mnt/c/voice_cloning/android/app/src/main/assets/vocab.txt");
    std::string content((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    tok.loadFromBuffer(content.data(), content.size());
    std::string full_text = "Some call me nature. Google LiteRT is fast and clear.";
    std::vector<int32_t> tokens = tok.encode(full_text, 128, -1);
    std::cout << "C++ tokens len: " << tokens.size() << std::endl;
    std::cout << "First 20 tokens: ";
    for (int i = 0; i < 20; ++i) std::cout << tokens[i] << " ";
    std::cout << std::endl;
    return 0;
}
