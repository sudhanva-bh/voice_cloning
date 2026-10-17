package com.indic.voice

import android.content.Context
import android.content.res.AssetFileDescriptor
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.channels.FileChannel

data class SynthesisResult(
    val audioSamples: FloatArray,
    val sampleRate: Int = 24000,
    val melTimeMs: Float,
    val diffusionTimeMs: Float,
    val vocosTimeMs: Float,
    val istftTimeMs: Float,
    val totalTimeMs: Float,
    val audioDurationSec: Float,
    val realTimeFactor: Float
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as SynthesisResult
        return audioSamples.contentEquals(other.audioSamples)
    }

    override fun hashCode(): Int {
        return audioSamples.contentHashCode()
    }
}

class LiteRTIndicEngine(private val context: Context) : AutoCloseable {

    companion object {
        init {
            try {
                System.loadLibrary("tensorflowlite_jni")
            } catch (ignored: Throwable) {}
            System.loadLibrary("litert_indic")
        }


        private const val DIT_MODEL_NAME = "indicf5_dit_int8.tflite"
        private const val VOCOS_MODEL_NAME = "indicf5_vocos_int8.tflite"
        private const val VOCAB_FILE_NAME = "vocab.txt"

        fun decodeWav(wavBytes: ByteArray): FloatArray {
            return nativeDecodeWav(wavBytes)
        }

        @JvmStatic
        private external fun nativeDecodeWav(wavBytes: ByteArray): FloatArray
    }

    private var enginePtr: Long = 0L

    suspend fun initialize(numThreads: Int = 4): Boolean = withContext(Dispatchers.IO) {
        if (enginePtr != 0L) return@withContext true

        val ditFd: AssetFileDescriptor = context.assets.openFd(DIT_MODEL_NAME)
        val ditBuffer = loadModelMmap(ditFd)
        val ditSize = ditFd.length

        val vocosFd: AssetFileDescriptor = context.assets.openFd(VOCOS_MODEL_NAME)
        val vocosBuffer = loadModelMmap(vocosFd)
        val vocosSize = vocosFd.length

        val vocabText = context.assets.open(VOCAB_FILE_NAME).bufferedReader(Charsets.UTF_8).use {
            it.readText()
        }

        enginePtr = nativeInit(
            ditBuffer, ditSize,
            vocosBuffer, vocosSize,
            vocabText,
            numThreads
        )

        return@withContext enginePtr != 0L
    }

    private fun loadModelMmap(afd: AssetFileDescriptor): ByteBuffer {
        val inputStream = FileInputStream(afd.fileDescriptor)
        val channel = inputStream.channel
        return channel.map(
            FileChannel.MapMode.READ_ONLY,
            afd.startOffset,
            afd.declaredLength
        )
    }

    suspend fun synthesize(
        refPcm: FloatArray,
        refText: String,
        targetText: String,
        numSteps: Int = 16,
        cfgStrength: Float = 2.0f,
        seed: Int = 42
    ): SynthesisResult = withContext(Dispatchers.Default) {
        check(enginePtr != 0L) { "LiteRTIndicEngine is not initialized!" }

        val telemetry = FloatArray(7)
        val pcmOut = nativeSynthesize(
            enginePtr,
            refPcm,
            refText,
            targetText,
            numSteps,
            cfgStrength,
            seed,
            telemetry
        )

        return@withContext SynthesisResult(
            audioSamples = pcmOut,
            sampleRate = 24000,
            melTimeMs = telemetry[0],
            diffusionTimeMs = telemetry[1],
            vocosTimeMs = telemetry[2],
            istftTimeMs = telemetry[3],
            totalTimeMs = telemetry[4],
            audioDurationSec = telemetry[5],
            realTimeFactor = telemetry[6]
        )
    }

    override fun close() {
        if (enginePtr != 0L) {
            nativeDestroy(enginePtr)
            enginePtr = 0L
        }
    }

    // Native JNI functions
    private external fun nativeInit(
        ditBuffer: ByteBuffer, ditSize: Long,
        vocosBuffer: ByteBuffer, vocosSize: Long,
        vocabStr: String,
        numThreads: Int
    ): Long

    private external fun nativeSynthesize(
        enginePtr: Long,
        refPcm: FloatArray,
        refText: String,
        targetText: String,
        numSteps: Int,
        cfgStrength: Float,
        seed: Int,
        outTelemetry: FloatArray
    ): FloatArray

    private external fun nativeDestroy(enginePtr: Long)
}
