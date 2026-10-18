package com.indic.voice.text

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

class MultilingualChunkerTest {

    private lateinit var chunker: MultilingualChunker

    @Before
    fun setUp() {
        chunker = MultilingualChunker(
            maxIndicChars = 44,
            maxEnglishChars = 60,
            minMergeChars = 12
        )
    }

    @Test
    fun testEmptyAndBlankInput() {
        assertTrue(chunker.split("").isEmpty())
        assertTrue(chunker.split("   ").isEmpty())
        assertTrue(chunker.split("\n\t  \n").isEmpty())
    }

    @Test
    fun testSingleShortEnglishSentenceReturnsOneChunk() {
        val input = "Hey there! Hope you are having a wonderful day."
        val chunks = chunker.split(input)

        assertEquals(1, chunks.size)
        assertEquals(0, chunks[0].index)
        assertEquals(input, chunks[0].text)
        assertTrue(chunks[0].isLast)
        assertTrue(chunks[0].estimatedFrames > 0)
        assertTrue(chunks[0].estimatedDurationSec > 0f)
    }

    @Test
    fun testMultiSentenceEnglishParagraph() {
        val input = "The morning sun rose gently above the hills. A cool breeze drifted through the pine forest. In the distance, a mountain stream flowed quietly."
        val chunks = chunker.split(input)

        assertTrue(chunks.size >= 3)
        // Verify all chunks are under the English max character budget (60)
        for (c in chunks) {
            assertTrue("Chunk too long (${c.text.length} chars): '${c.text}'", c.text.length <= 60)
        }
        // Verify sequence indexing and isLast
        for (i in chunks.indices) {
            assertEquals(i, chunks[i].index)
            if (i == chunks.size - 1) {
                assertTrue(chunks[i].isLast)
            } else {
                assertFalse(chunks[i].isLast)
            }
        }
    }

    @Test
    fun testHindiTextWithDandaAndCommas() {
        val input = "नमस्ते, यह मेरी आवाज का परीक्षण है। आज मौसम बहुत सुहावना है और प्रकृति चारों ओर हरी-भरी दिखाई दे रही है। क्या आप आज शाम को टहलने चलेंगे?"
        val chunks = chunker.split(input)

        assertTrue(chunks.size >= 3)
        for (c in chunks) {
            assertTrue("Indic chunk exceeds 44 chars (${c.text.length}): '${c.text}'", c.text.length <= 44)
        }
    }

    @Test
    fun testTeluguTextWithCompoundClauses() {
        val input = "నమస్కారం! ఈ రోజు వాతావరణం చాలా ఆహ్లాదకరంగా మరియు చల్లగా ఉంది. కృత్రిమ మేధస్సు నేరుగా మీ మొబైల్ ఫోన్‌లో పనిచేస్తోంది. ఈ వాయిస్ క్లోనింగ్ డెమో విన్నందుకు ధన్యవాదాలు."
        val chunks = chunker.split(input)

        assertTrue(chunks.size >= 3)
        for (c in chunks) {
            assertTrue("Telugu chunk exceeds 42-44 chars (${c.text.length}): '${c.text}'", c.text.length <= 44)
        }
    }

    @Test
    fun testTamilTextWithClauses() {
        val input = "வணக்கம்! இன்று வானிலை மிகவும் இனிமையாகவும் தென்றலாகவும் இருக்கிறது. செயற்கை நுண்ணறிவு நேரடியாக உங்கள் போனில் இயங்குகிறது. இந்த குரல் சோதனையைக் கேட்டதற்கு மிக்க நன்றி."
        val chunks = chunker.split(input)

        assertTrue(chunks.size >= 3)
        for (c in chunks) {
            assertTrue("Tamil chunk exceeds 44 chars (${c.text.length}): '${c.text}'", c.text.length <= 44)
        }
    }

    @Test
    fun testAbbreviationsDoNotSplit() {
        val input = "Dr. Smith met Mr. Brown at the speech research lab."
        val chunks = chunker.split(input)

        assertEquals(1, chunks.size)
        assertTrue(chunks[0].text.contains("Dr."))
        assertTrue(chunks[0].text.contains("Mr."))
    }

    @Test
    fun testDecimalsDoNotSplit() {
        val input = "The value of pi is approximately 3.1415 and the step size is 0.5 units."
        val chunks = chunker.split(input)

        // Decimals should stay intact without spurious sentence splits on "."
        for (c in chunks) {
            if (c.text.contains("3.1415")) {
                assertTrue(c.text.contains("3.1415"))
            }
        }
        assertTrue(chunks.any { it.text.contains("3.1415") })
    }

    @Test
    fun testLongUnbrokenSentenceSplitsAtWordBoundaries() {
        // 120+ characters with no punctuation whatsoever
        val input = "This is a continuous run on sentence that has absolutely no punctuation anywhere in the middle to see how the chunker handles unbroken words gracefully"
        val chunks = chunker.split(input)

        assertTrue("Should split unbroken sentence into multiple chunks", chunks.size >= 2)
        for (c in chunks) {
            assertTrue("Chunk '${c.text}' length ${c.text.length} exceeds 60", c.text.length <= 60)
        }
    }

    @Test
    fun testMicroFragmentMerging() {
        // "Yes." is only 4 characters, should merge with next sentence if within budget
        val input = "Yes. Everything is working correctly now."
        val chunks = chunker.split(input)

        assertEquals("Tiny fragment should be merged with adjacent sentence", 1, chunks.size)
        assertEquals("Yes. Everything is working correctly now.", chunks[0].text)
    }
}
