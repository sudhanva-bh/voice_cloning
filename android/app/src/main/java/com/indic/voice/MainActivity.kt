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

    override fun onDestroy() {
        super.onDestroy()
        audioPlayer.stop()
        engine.close()
    }
}
