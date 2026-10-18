package com.indic.voice.text

/**
 * Represents an individual synthesizable audio chunk for IndicF5 LiteRT.
 *
 * @param index 0-based sequence index.
 * @param text The exact text to synthesize in this chunk.
 * @param estimatedFrames Estimated mel frames required for synthesis.
 * @param estimatedDurationSec Estimated audio duration in seconds.
 * @param isLast True if this is the final chunk in the sequence.
 */
data class SpeechChunk(
    val index: Int,
    val text: String,
    val estimatedFrames: Int,
    val estimatedDurationSec: Float,
    val isLast: Boolean
)

/**
 * Intelligent multilingual text splitter and chunker for IndicF5 LiteRT.
 *
 * Guarantees that every generated chunk strictly fits within the static 512-frame
 * window of the LiteRT INT8 DiT model (~3.05s target audio budget, <= 286 frames).
 *
 * Supports Indic scripts (Devanagari, Telugu, Tamil, Kannada) and Latin (English)
 * with script-calibrated character limits, abbreviation preservation, and a
 * 3-tier hierarchical fallback (Sentence -> Clause -> Word).
 */
class MultilingualChunker(
    private val maxIndicChars: Int = 44,
    private val maxEnglishChars: Int = 60,
    private val minMergeChars: Int = 12
) {

    companion object {
        // Protected abbreviations that should not trigger sentence splits
        private val ABBREVIATIONS = listOf(
            "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "Sr.", "Jr.",
            "vs.", "e.g.", "i.e.", "etc.", "approx.", "govt."
        )

        private const val DOT_PLACEHOLDER = "@@DOT@@"
    }

    /**
     * Splits arbitrary input text into a list of safe [SpeechChunk]s.
     */
    fun split(rawText: String): List<SpeechChunk> {
        val trimmed = rawText.trim()
        if (trimmed.isEmpty()) return emptyList()

        // 1. Detect dominant script & set max characters
        val isIndic = containsIndicScript(trimmed)
        val maxChars = if (isIndic) maxIndicChars else maxEnglishChars
        val framesPerChar = if (isIndic) 6.5f else 4.5f

        // 2. Protect decimals and common abbreviations
        val sanitized = protectNonSentenceDots(trimmed)

        // 3. Tier 1: Split by terminal sentence punctuation [.!?।॥\n]
        val tier1Segments = splitTier1SentenceBoundaries(sanitized)

        // 4. Tier 2: Split oversize sentences by clause boundaries [,;:\u2014\u2013\-]
        val tier2Segments = mutableListOf<String>()
        for (seg in tier1Segments) {
            if (seg.length <= maxChars) {
                tier2Segments.add(seg)
            } else {
                tier2Segments.addAll(splitTier2ClauseBoundaries(seg, maxChars))
            }
        }

        // 5. Tier 3: Split any remaining oversize segments by word boundaries
        val tier3Segments = mutableListOf<String>()
        for (seg in tier2Segments) {
            if (seg.length <= maxChars) {
                tier3Segments.add(seg)
            } else {
                tier3Segments.addAll(splitTier3WordBoundaries(seg, maxChars))
            }
        }

        // 6. Restore protected dots
        val unmaskedSegments = tier3Segments
            .map { it.replace(DOT_PLACEHOLDER, ".") }
            .map { it.trim() }
            .filter { it.isNotEmpty() }

        if (unmaskedSegments.isEmpty()) return emptyList()

        // 7. Micro-fragment merging: coalesce tiny chunks (< minMergeChars)
        val mergedSegments = coalesceMicroFragments(unmaskedSegments, maxChars)

        // 8. Construct SpeechChunk objects with telemetry estimation
        val total = mergedSegments.size
        return mergedSegments.mapIndexed { idx, text ->
            val estFrames = (text.length * framesPerChar).toInt().coerceAtLeast(30)
            val estSec = estFrames * 256f / 24000f
            SpeechChunk(
                index = idx,
                text = text,
                estimatedFrames = estFrames,
                estimatedDurationSec = estSec,
                isLast = (idx == total - 1)
            )
        }
    }

    /**
     * Checks if text contains Indic Unicode script codepoints.
     * Devanagari (0900-097F), Tamil (0B80-0BFF), Telugu (0C00-0C7F), Kannada (0C80-0CFF).
     */
    private fun containsIndicScript(text: String): Boolean {
        for (c in text) {
            val code = c.code
            if (code in 0x0900..0x097F || // Devanagari (Hindi, Marathi)
                code in 0x0B80..0x0BFF || // Tamil
                code in 0x0C00..0x0C7F || // Telugu
                code in 0x0C80..0x0CFF    // Kannada
            ) {
                return true
            }
        }
        return false
    }

    /**
     * Protects decimals (e.g. 3.14) and abbreviations (e.g. Dr., Mr.) from sentence splitting.
     */
    private fun protectNonSentenceDots(text: String): String {
        var result = text

        // Protect decimals: digits.digits
        result = result.replace(Regex("(\\d+)\\.(\\d+)"), "$1${DOT_PLACEHOLDER}$2")

        // Protect common abbreviations
        for (abbr in ABBREVIATIONS) {
            val safe = abbr.replace(".", DOT_PLACEHOLDER)
            result = result.replace(Regex("(?i)\\b" + Regex.escape(abbr)), safe)
        }

        return result
    }

    /**
     * Tier 1: Splits by terminal sentence punctuation [.!?।॥\n]
     */
    private fun splitTier1SentenceBoundaries(text: String): List<String> {
        // Regex matches terminal punctuation, keeping it attached to the preceding sentence
        val regex = Regex("(?<=[.!?\u0964\u0965\\n])\\s+")
        return text.split(regex)
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }

    /**
     * Tier 2: Splits a segment that exceeds maxChars by clause punctuation [,;:\u2014\u2013\-]
     */
    private fun splitTier2ClauseBoundaries(sentence: String, maxChars: Int): List<String> {
        val clauseRegex = Regex("(?<=[,;:—–\\-])\\s+")
        val candidateClauses = sentence.split(clauseRegex)
            .map { it.trim() }
            .filter { it.isNotEmpty() }

        if (candidateClauses.size <= 1) {
            return listOf(sentence)
        }

        val packed = mutableListOf<String>()
        var current = StringBuilder()

        for (clause in candidateClauses) {
            if (current.isEmpty()) {
                current.append(clause)
            } else if (current.length + 1 + clause.length <= maxChars) {
                current.append(" ").append(clause)
            } else {
                packed.add(current.toString())
                current = StringBuilder(clause)
            }
        }
        if (current.isNotEmpty()) {
            packed.add(current.toString())
        }

        return packed
    }

    /**
     * Tier 3: Splits a segment that still exceeds maxChars at word boundaries.
     */
    private fun splitTier3WordBoundaries(segment: String, maxChars: Int): List<String> {
        val words = segment.split(Regex("\\s+")).filter { it.isNotEmpty() }
        val chunks = mutableListOf<String>()
        var current = StringBuilder()

        for (w in words) {
            if (current.isEmpty()) {
                if (w.length <= maxChars) {
                    current.append(w)
                } else {
                    // Single word exceeds maxChars (e.g. extremely long unbroken string)
                    var remaining = w
                    while (remaining.length > maxChars) {
                        chunks.add(remaining.substring(0, maxChars))
                        remaining = remaining.substring(maxChars)
                    }
                    if (remaining.isNotEmpty()) {
                        current.append(remaining)
                    }
                }
            } else if (current.length + 1 + w.length <= maxChars) {
                current.append(" ").append(w)
            } else {
                chunks.add(current.toString())
                current = StringBuilder(w)
            }
        }
        if (current.isNotEmpty()) {
            chunks.add(current.toString())
        }

        return chunks
    }

    /**
     * Merges very small fragments (< minMergeChars) with adjacent chunks
     * as long as the combined length does not exceed maxChars.
     */
    private fun coalesceMicroFragments(segments: List<String>, maxChars: Int): List<String> {
        if (segments.size <= 1) return segments

        val result = mutableListOf<String>()
        var i = 0

        while (i < segments.size) {
            var current = segments[i]

            // If current chunk is very short and there's a next chunk, try merging forward
            if (current.length < minMergeChars && i + 1 < segments.size) {
                val next = segments[i + 1]
                if (current.length + 1 + next.length <= maxChars) {
                    current = "$current $next"
                    i++ // Skip next since merged
                }
            }

            // Alternatively, if current chunk is very short and previous chunk has room, merge backward
            if (current.length < minMergeChars && result.isNotEmpty()) {
                val lastIdx = result.size - 1
                val prev = result[lastIdx]
                if (prev.length + 1 + current.length <= maxChars) {
                    result[lastIdx] = "$prev $current"
                    i++
                    continue
                }
            }

            result.add(current)
            i++
        }

        return result
    }
}
