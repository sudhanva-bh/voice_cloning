package com.indic.voice.audio

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import kotlin.math.abs

class WaveformStitcherTest {

    private lateinit var stitcher: WaveformStitcher

    @Before
    fun setUp() {
        stitcher = WaveformStitcher(
            sampleRate = 24000,
            interSentenceSilenceMs = 120, // 2880 samples
            fadeDurationMs = 5.0f,         // 120 samples
            targetPeak = 0.95f
        )
    }

    @Test
    fun testEmptyInputReturnsEmptyArray() {
        val res = stitcher.stitch(emptyList())
        assertEquals(0, res.size)

        val res2 = stitcher.stitch(listOf(FloatArray(0), FloatArray(0)))
        assertEquals(0, res2.size)
    }

    @Test
    fun testSingleChunkStitching() {
        val chunk = FloatArray(4800) { 0.5f }
        val stitched = stitcher.stitch(listOf(chunk))

        assertEquals(4800, stitched.size)
        // Verify peak normalized to ~0.95
        var maxVal = 0.0f
        for (s in stitched) {
            if (abs(s) > maxVal) maxVal = abs(s)
        }
        assertEquals(0.95f, maxVal, 0.001f)

        // Verify boundary fade-in at start (sample 0 should be 0.0)
        assertEquals(0.0f, stitched[0], 0.001f)
        // Last sample should be close to 0.0
        assertTrue("Last sample should be faded towards 0", abs(stitched[stitched.size - 1]) < 0.1f)
    }

    @Test
    fun testMultiChunkLengthAndSilenceSpacing() {
        val chunk1 = FloatArray(2400) { 0.4f }
        val chunk2 = FloatArray(3600) { 0.6f }
        val chunk3 = FloatArray(1200) { 0.3f }

        val stitched = stitcher.stitch(listOf(chunk1, chunk2, chunk3))

        // Expected length: 2400 + 3600 + 1200 + 2 * 2880 = 7200 + 5760 = 12960 samples
        val expectedLength = (2400 + 3600 + 1200) + 2 * stitcher.silenceSamples
        assertEquals(expectedLength, stitched.size)

        // Verify silence gap between chunk1 and chunk2 (offset 2400 to 2400 + 2880)
        val silenceStart = 2400
        val silenceEnd = 2400 + stitcher.silenceSamples
        for (i in silenceStart until silenceEnd) {
            assertEquals("Sample at silence index $i must be zero", 0.0f, stitched[i], 0.0001f)
        }

        // Verify silence gap between chunk2 and chunk3
        val silence2Start = 2400 + stitcher.silenceSamples + 3600
        val silence2End = silence2Start + stitcher.silenceSamples
        for (i in silence2Start until silence2End) {
            assertEquals("Sample at silence index $i must be zero", 0.0f, stitched[i], 0.0001f)
        }
    }

    @Test
    fun testGlobalPeakNormalization() {
        val quietChunk = FloatArray(2400) { 0.1f }
        val loudChunk = FloatArray(2400) { 0.8f }

        val stitched = stitcher.stitch(listOf(quietChunk, loudChunk))

        var maxPeak = 0.0f
        for (s in stitched) {
            if (abs(s) > maxPeak) maxPeak = abs(s)
        }
        assertEquals(0.95f, maxPeak, 0.001f)
    }

    @Test
    fun testPerformanceOnLongAudio() {
        // 15 chunks of 2.0s audio each = 30 seconds total speech
        val chunks = List(15) {
            FloatArray(48000) { i -> (i % 100) / 100f }
        }

        val start = System.nanoTime()
        val stitched = stitcher.stitch(chunks)
        val elapsedMs = (System.nanoTime() - start) / 1_000_000.0

        assertTrue("Stitching 30s audio should take under 25ms, took ${elapsedMs}ms", elapsedMs < 25.0)
        assertTrue(stitched.isNotEmpty())
    }
}
