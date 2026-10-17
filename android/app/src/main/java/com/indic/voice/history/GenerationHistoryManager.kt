package com.indic.voice.history

import android.content.Context
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class GenerationHistoryManager(private val context: Context) {

    private val generatedDir: File
        get() {
            val dir = File(context.filesDir, "generated")
            if (!dir.exists()) dir.mkdirs()
            return dir
        }

    fun saveGeneratedClip(pcm: FloatArray, rtf: Float, rssMB: Int, sampleRate: Int = 24000): File {
        val now = Date()
        val dateFormat = SimpleDateFormat("dd_MM_yyyy__HH_mm", Locale.getDefault())
        val timeStamp = dateFormat.format(now)
        val rtfStr = String.format(Locale.US, "%.2f", rtf)
        val rssStr = rssMB.toString()
        val timestampMs = System.currentTimeMillis()

        val fileName = "generated_${timeStamp}_rtf_${rtfStr}_rss_${rssStr}_${timestampMs}.wav"
        val outFile = File(generatedDir, fileName)

        writePcmToWav(outFile, pcm, sampleRate)
        return outFile
    }

    fun loadHistory(): List<GeneratedClipItem> {
        val files = generatedDir.listFiles { file ->
            file.isFile && file.name.startsWith("generated_") && file.name.endsWith(".wav")
        } ?: return emptyList()

        return files.map { file ->
            val filename = file.name
            val displayTitle = extractDisplayTitle(filename)
            val rtf = extractRtf(filename)
            val rss = extractRss(filename)
            GeneratedClipItem(
                file = file,
                displayTitle = displayTitle,
                rtf = rtf,
                rssMB = rss,
                timestampMs = file.lastModified()
            )
        }.sortedByDescending { it.timestampMs }
    }

    fun deleteClip(file: File): Boolean {
        return if (file.exists()) {
            file.delete()
        } else false
    }

    private fun extractDisplayTitle(filename: String): String {
        val match = Regex("""(generated_\d{2}_\d{2}_\d{4}__\d{2}_\d{2})""").find(filename)
        if (match != null) {
            return match.groupValues[1]
        }
        return filename
            .replace(Regex("""_rtf_[0-9.]+_rss_[0-9]+_"""), "_")
            .replace(Regex("""_\d+\.wav$"""), "")
            .replace(".wav", "")
    }

    private fun extractRtf(filename: String): String? {
        val match = Regex("""_rtf_([0-9.]+)_""").find(filename)
        return match?.groupValues?.get(1)
    }

    private fun extractRss(filename: String): String? {
        val match = Regex("""_rss_([0-9]+)_""").find(filename)
        return match?.groupValues?.get(1)
    }

    private fun writePcmToWav(file: File, pcm: FloatArray, sampleRate: Int) {
        val totalAudioLen = pcm.size * 2
        val totalDataLen = totalAudioLen + 36
        val channels = 1
        val byteRate = sampleRate * channels * 2

        FileOutputStream(file).use { out ->
            val header = ByteArray(44)
            header[0] = 'R'.code.toByte(); header[1] = 'I'.code.toByte(); header[2] = 'F'.code.toByte(); header[3] = 'F'.code.toByte()
            header[4] = (totalDataLen and 0xff).toByte()
            header[5] = ((totalDataLen shr 8) and 0xff).toByte()
            header[6] = ((totalDataLen shr 16) and 0xff).toByte()
            header[7] = ((totalDataLen shr 24) and 0xff).toByte()
            header[8] = 'W'.code.toByte(); header[9] = 'A'.code.toByte(); header[10] = 'V'.code.toByte(); header[11] = 'E'.code.toByte()
            header[12] = 'f'.code.toByte(); header[13] = 'm'.code.toByte(); header[14] = 't'.code.toByte(); header[15] = ' '.code.toByte()
            header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0
            header[20] = 1; header[21] = 0 // PCM format
            header[22] = channels.toByte(); header[23] = 0
            header[24] = (sampleRate and 0xff).toByte()
            header[25] = ((sampleRate shr 8) and 0xff).toByte()
            header[26] = ((sampleRate shr 16) and 0xff).toByte()
            header[27] = ((sampleRate shr 24) and 0xff).toByte()
            header[28] = (byteRate and 0xff).toByte()
            header[29] = ((byteRate shr 8) and 0xff).toByte()
            header[30] = ((byteRate shr 16) and 0xff).toByte()
            header[31] = ((byteRate shr 24) and 0xff).toByte()
            header[32] = (channels * 2).toByte(); header[33] = 0
            header[34] = 16; header[35] = 0
            header[36] = 'd'.code.toByte(); header[37] = 'a'.code.toByte(); header[38] = 't'.code.toByte(); header[39] = 'a'.code.toByte()
            header[40] = (totalAudioLen and 0xff).toByte()
            header[41] = ((totalAudioLen shr 8) and 0xff).toByte()
            header[42] = ((totalAudioLen shr 16) and 0xff).toByte()
            header[43] = ((totalAudioLen shr 24) and 0xff).toByte()
            out.write(header)

            val pcmBytes = ByteArray(pcm.size * 2)
            for (i in pcm.indices) {
                val clamped = pcm[i].coerceIn(-1.0f, 1.0f)
                val s16 = (clamped * 32767.0f).toInt().toShort()
                pcmBytes[i * 2] = (s16.toInt() and 0xff).toByte()
                pcmBytes[i * 2 + 1] = ((s16.toInt() shr 8) and 0xff).toByte()
            }
            out.write(pcmBytes)
        }
    }
}
