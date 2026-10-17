#ifndef INDIC_TOKENIZER_H
#define INDIC_TOKENIZER_H

#include <string>
#include <vector>
#include <unordered_map>
#include <cstdint>

namespace indic {

class IndicTokenizer {
public:
    IndicTokenizer() = default;
    
    // Load vocabulary from string buffer (e.g. from APK assets)
    bool loadFromBuffer(const char* buffer, size_t buffer_len);

    // Tokenize full UTF-8 text (handles multi-byte UTF-8 for Indic scripts)
    // Returns tokens padded to max_len (default 128) with pad_value (-1)
    std::vector<int32_t> encode(const std::string& text, size_t max_len = 128, int32_t pad_value = -1) const;

    size_t vocabSize() const { return char_to_id_.size(); }

private:
    std::unordered_map<std::string, int32_t> char_to_id_;
};

} // namespace indic

#endif // INDIC_TOKENIZER_H
