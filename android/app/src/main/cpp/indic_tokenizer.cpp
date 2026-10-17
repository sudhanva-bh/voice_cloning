#include "indic_tokenizer.h"
#include <sstream>
#include <iostream>

namespace indic {

bool IndicTokenizer::loadFromBuffer(const char* buffer, size_t buffer_len) {
    char_to_id_.clear();
    std::string text(buffer, buffer_len);
    std::istringstream stream(text);
    std::string line;
    int32_t idx = 0;

    while (std::getline(stream, line)) {
        // Strip trailing \r if Windows line endings
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        char_to_id_[line] = idx++;
    }
    return !char_to_id_.empty();
}

std::vector<int32_t> IndicTokenizer::encode(const std::string& text, size_t max_len, int32_t pad_value) const {
    std::vector<int32_t> tokens;
    tokens.reserve(max_len);

    size_t i = 0;
    while (i < text.length() && tokens.size() < max_len) {
        unsigned char c = static_cast<unsigned char>(text[i]);
        size_t char_len = 1;

        if ((c & 0x80) == 0) {
            char_len = 1;
        } else if ((c & 0xE0) == 0xC0) {
            char_len = 2;
        } else if ((c & 0xF0) == 0xE0) {
            char_len = 3;
        } else if ((c & 0xF8) == 0xF0) {
            char_len = 4;
        }

        if (i + char_len > text.length()) {
            break; // Truncated UTF-8 sequence
        }

        std::string utf8_char = text.substr(i, char_len);
        i += char_len;

        auto it = char_to_id_.find(utf8_char);
        if (it != char_to_id_.end()) {
            tokens.push_back(it->second);
        } else {
            tokens.push_back(pad_value);
        }
    }

    // Pad to max_len
    while (tokens.size() < max_len) {
        tokens.push_back(pad_value);
    }

    return tokens;
}

} // namespace indic
