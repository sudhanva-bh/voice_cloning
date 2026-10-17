package com.indic.voice

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.indic.voice.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val engine by lazy { LiteRTIndicEngine(this) }
    private val audioPlayer by lazy { AudioPlayer() }

    private var refPcm: FloatArray? = null
    private var lastGeneratedPcm: FloatArray? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupQuickPresets()
        setupListeners()
        initializeEngineAndReference()
    }

    private fun setupQuickPresets() {
        binding.btnQuickEn.setOnClickListener {
            binding.etTargetText.setText("Google LiteRT is fast and clear.")
        }
        binding.btnQuickHi.setOnClickListener {
            binding.etTargetText.setText("यह एक वॉइस क्लोनिंग का परीक्षण है।")
        }
        binding.btnQuickTe.setOnClickListener {
            binding.etTargetText.setText("ఇది గూగుల్ లైట్-ఆర్టీతో వాయిస్ క్లోనింగ్ పరీక్ష.")
        }
        binding.btnQuickTa.setOnClickListener {
            binding.etTargetText.setText("கூகிள் லைட்-ஆர்டி தொழில்நுட்பம் மூலம் குரல் உருவாக்கம்.")
        }
    }

    private fun setupListeners() {
        binding.btnSynthesize.setOnClickListener {
            synthesizeCurrentText()
        }

        binding.btnPlay.setOnClickListener {
            lastGeneratedPcm?.let { samples ->
                lifecycleScope.launch {
                    audioPlayer.play(samples, 24000)
                }
            }
        }
    }

    private fun initializeEngineAndReference() {
        binding.btnSynthesize.isEnabled = false
        binding.progressBar.visibility = View.VISIBLE
        binding.tvLatencyInfo.text = "Initializing Google LiteRT Engine (INT8)..."

        lifecycleScope.launch {
            try {
                val ok = engine.initialize(numThreads = 4)
                if (!ok) {
                    binding.tvLatencyInfo.text = "Failed to initialize LiteRT Engine"
                    Toast.makeText(this@MainActivity, "Engine init failed", Toast.LENGTH_LONG).show()
                    return@launch
                }

                // Load reference WAV from assets
                val wavBytes = withContext(Dispatchers.IO) {
                    assets.open("samples/ref_en.wav").use { it.readBytes() }
                }
                refPcm = LiteRTIndicEngine.decodeWav(wavBytes)

                val vmrss = TelemetryMonitor.getResidentMemoryMB()
                binding.tvMemoryInfo.text = "Resident Memory (VmRSS): $vmrss MB / 600 MB Target"
                binding.tvLatencyInfo.text = "Engine Ready. Tap Synthesize."
                binding.btnSynthesize.isEnabled = true
            } catch (e: Exception) {
                binding.tvLatencyInfo.text = "Error: ${e.localizedMessage}"
            } finally {
                binding.progressBar.visibility = View.GONE
            }
        }
    }

    private fun synthesizeCurrentText() {
        val pcm = refPcm ?: return
        val refText = binding.etRefText.text.toString().trim()
        val targetText = binding.etTargetText.text.toString().trim()

        if (targetText.isEmpty()) {
            Toast.makeText(this, "Please enter target text", Toast.LENGTH_SHORT).show()
            return
        }

        val steps = when (binding.rgSteps.checkedRadioButtonId) {
            binding.rbStep8.id -> 8
            binding.rbStep24.id -> 24
            else -> 16
        }

        binding.btnSynthesize.isEnabled = false
        binding.btnPlay.isEnabled = false
        binding.progressBar.visibility = View.VISIBLE
        binding.tvLatencyInfo.text = "Solving Flow Matching ODE ($steps steps)..."

        lifecycleScope.launch {
            try {
                val result = engine.synthesize(
                    refPcm = pcm,
                    refText = refText,
                    targetText = targetText,
                    numSteps = steps,
                    cfgStrength = 2.0f
                )

                lastGeneratedPcm = result.audioSamples
                val vmrss = TelemetryMonitor.getResidentMemoryMB()

                binding.tvMemoryInfo.text = "Resident Memory (VmRSS): $vmrss MB / 600 MB Target"
                binding.tvLatencyInfo.text = "Mel: ${result.melTimeMs.toInt()}ms | DiT: ${result.diffusionTimeMs.toInt()}ms | Vocos: ${result.vocosTimeMs.toInt()}ms | Total: ${result.totalTimeMs.toInt()}ms"
                binding.tvRtfInfo.text = "Real-Time Factor: ${String.format("%.2f", result.realTimeFactor)}x (${String.format("%.2f", result.audioDurationSec)}s audio)"

                binding.btnPlay.isEnabled = true
                try {
                    val wavFile = java.io.File(filesDir, "generated_voice.wav")
                    savePcmToWav(wavFile, result.audioSamples, 24000)
                } catch (ignored: Exception) {}
                audioPlayer.play(result.audioSamples, 24000)
            } catch (e: Exception) {
                binding.tvLatencyInfo.text = "Synthesis Error: ${e.localizedMessage}"
                Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                binding.btnSynthesize.isEnabled = true
                binding.progressBar.visibility = View.GONE
            }
        }
    }

    private fun savePcmToWav(file: java.io.File, pcm: FloatArray, sampleRate: Int) {
        val totalAudioLen = pcm.size * 2
        val totalDataLen = totalAudioLen + 36
        val channels = 1
        val byteRate = sampleRate * channels * 2

        file.outputStream().use { out ->
            val header = ByteArray(44)
            header[0] = 'R'.code.toByte(); header[1] = 'I'.code.toByte(); header[2] = 'F'.code.toByte(); header[3] = 'F'.code.toByte()
            header[4] = (totalDataLen and 0xff).toByte()
            header[5] = ((totalDataLen shr 8) and 0xff).toByte()
            header[6] = ((totalDataLen shr 16) and 0xff).toByte()
            header[7] = ((totalDataLen shr 24) and 0xff).toByte()
            header[8] = 'W'.code.toByte(); header[9] = 'A'.code.toByte(); header[10] = 'V'.code.toByte(); header[11] = 'E'.code.toByte()
            header[12] = 'f'.code.toByte(); header[13] = 'm'.code.toByte(); header[14] = 't'.code.toByte(); header[15] = ' '.code.toByte()
            header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0
            header[20] = 1; header[21] = 0
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

    override fun onDestroy() {
        super.onDestroy()
        audioPlayer.stop()
        engine.close()
    }
}
