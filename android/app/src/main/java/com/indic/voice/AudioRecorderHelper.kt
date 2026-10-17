package com.indic.voice

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import java.io.File
import java.io.FileOutputStream
import java.io.RandomAccessFile
import java.util.concurrent.atomic.AtomicBoolean

class AudioRecorderHelper {

    companion object {
        private const val TAG = "AudioRecorderHelper"
        const val SAMPLE_RATE = 24000
        private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        private const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
    }

    private var audioRecord: AudioRecord? = null
    private var recordingThread: Thread? = null
    private val isRecordingAtomic = AtomicBoolean(false)
    private var currentOutputFile: File? = null

    val isRecording: Boolean
        get() = isRecordingAtomic.get()

    @SuppressLint("MissingPermission")
    fun startRecording(outputWavFile: File): Boolean {
        if (isRecordingAtomic.get()) {
            Log.w(TAG, "Recording already in progress")
            return false
        }

        val minBufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)
        if (minBufferSize == AudioRecord.ERROR || minBufferSize == AudioRecord.ERROR_BAD_VALUE) {
            Log.e(TAG, "Invalid AudioRecord buffer size: $minBufferSize")
            return false
        }

        val bufferSize = maxOf(minBufferSize * 2, 4096)

        try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "AudioRecord failed to initialize")
                audioRecord?.release()
                audioRecord = null
                return false
            }

            currentOutputFile = outputWavFile
            outputWavFile.parentFile?.mkdirs()
            if (outputWavFile.exists()) outputWavFile.delete()

            isRecordingAtomic.set(true)
            audioRecord?.startRecording()

            recordingThread = Thread {
                writeAudioDataToWav(outputWavFile, bufferSize)
            }.apply {
                priority = Thread.MAX_PRIORITY
                start()
            }

            Log.i(TAG, "Started recording 24kHz mono to ${outputWavFile.absolutePath}")
            return true
        } catch (e: Exception) {
            Log.e(TAG, "Error starting recording: ${e.message}", e)
            isRecordingAtomic.set(false)
            audioRecord?.release()
            audioRecord = null
            return false
        }
    }

    fun stopRecording(): File? {
        if (!isRecordingAtomic.get()) {
            return null
        }

        isRecordingAtomic.set(false)

        try {
            audioRecord?.stop()
            audioRecord?.release()
            audioRecord = null
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping AudioRecord: ${e.message}")
        }

        try {
            recordingThread?.join(2000)
            recordingThread = null
        } catch (e: InterruptedException) {
            Log.w(TAG, "Recording thread join interrupted")
        }

        val file = currentOutputFile
        if (file != null && file.exists() && file.length() > 44) {
            Log.i(TAG, "Finished recording WAV: ${file.length()} bytes")
            return file
        }
        return null
    }

    private fun writeAudioDataToWav(file: File, bufferSize: Int) {
        val data = ByteArray(bufferSize)
        var fos: FileOutputStream? = null

        try {
            fos = FileOutputStream(file)
            // Write placeholder 44-byte WAV header
            fos.write(ByteArray(44))

            var totalBytesRead = 0L
            while (isRecordingAtomic.get()) {
                val read = audioRecord?.read(data, 0, bufferSize) ?: -1
                if (read > 0) {
                    fos.write(data, 0, read)
                    totalBytesRead += read
                }
            }
            fos.flush()
            fos.close()
            fos = null

            // Update WAV header with correct total data length
            writeWavHeader(file, totalBytesRead, SAMPLE_RATE, 1, 16)
        } catch (e: Exception) {
            Log.e(TAG, "Error writing audio data: ${e.message}", e)
        } finally {
            try { fos?.close() } catch (ignored: Exception) {}
        }
    }

    private fun writeWavHeader(
        file: File,
        audioLength: Long,
        sampleRate: Int,
        channels: Int,
        bitsPerSample: Int
    ) {
        val totalDataLen = audioLength + 36
        val byteRate = sampleRate * channels * bitsPerSample / 8

        RandomAccessFile(file, "rw").use { raf ->
            raf.seek(0)
            val header = ByteArray(44)
            header[0] = 'R'.code.toByte(); header[1] = 'I'.code.toByte(); header[2] = 'F'.code.toByte(); header[3] = 'F'.code.toByte()
            header[4] = (totalDataLen and 0xff).toByte()
            header[5] = ((totalDataLen shr 8) and 0xff).toByte()
            header[6] = ((totalDataLen shr 16) and 0xff).toByte()
            header[7] = ((totalDataLen shr 24) and 0xff).toByte()
            header[8] = 'W'.code.toByte(); header[9] = 'A'.code.toByte(); header[10] = 'V'.code.toByte(); header[11] = 'E'.code.toByte()
            header[12] = 'f'.code.toByte(); header[13] = 'm'.code.toByte(); header[14] = 't'.code.toByte(); header[15] = ' '.code.toByte()
            header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0 // subchunk1 size
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
            header[32] = ((channels * bitsPerSample) / 8).toByte(); header[33] = 0
            header[34] = bitsPerSample.toByte(); header[35] = 0
            header[36] = 'd'.code.toByte(); header[37] = 'a'.code.toByte(); header[38] = 't'.code.toByte(); header[39] = 'a'.code.toByte()
            header[40] = (audioLength and 0xff).toByte()
            header[41] = ((audioLength shr 8) and 0xff).toByte()
            header[42] = ((audioLength shr 16) and 0xff).toByte()
            header[43] = ((audioLength shr 24) and 0xff).toByte()
            raf.write(header)
        }
    }
}
