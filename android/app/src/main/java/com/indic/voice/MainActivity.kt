package com.indic.voice

import android.Manifest
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.widget.addTextChangedListener
import androidx.lifecycle.lifecycleScope
import com.indic.voice.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val engine by lazy { LiteRTIndicEngine(this) }
    private val audioPlayer by lazy { AudioPlayer() }
    private val recorderHelper by lazy { AudioRecorderHelper() }

    private var refPcm: FloatArray? = null
    private var refAudioPath: String? = null
    private var refAudioName: String = "ref_en.wav"
    private var lastGeneratedPcm: FloatArray? = null

    private var previewMediaPlayer: MediaPlayer? = null
    private var isPreviewPlaying = false

    // Permission launcher for Microphone recording
    private val requestAudioPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            startLiveRecording()
        } else {
            Toast.makeText(this, "Microphone permission is required to record voice", Toast.LENGTH_SHORT).show()
        }
    }

    // File picker launcher for external audio upload
    private val pickAudioLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        if (uri != null) {
            handlePickedAudioUri(uri)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupStep1Listeners()
        setupStep2RecordingAndPicker()
        setupStep3TargetAndLanguage()
        setupStep4Output()
        setupValidationListeners()

        initializeEngineAndDefaultReference()
    }

    private fun setupStep1Listeners() {
        binding.btnClearRefText.setOnClickListener {
            binding.etRefText.setText("")
            updateValidationState()
        }

        binding.btnExampleScripts.setOnClickListener {
            Toast.makeText(this, "Example Scripts modal will be integrated in Phase 3", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupStep2RecordingAndPicker() {
        // Record audio button
        binding.btnRecordAudio.setOnClickListener {
            toggleRecording()
        }

        // Re-record button inside ready state
        binding.btnReRecordAudio.setOnClickListener {
            binding.llRefAudioReady.visibility = View.GONE
            binding.llRefAudioNotReady.visibility = View.VISIBLE
            toggleRecording()
        }

        // Upload file button
        binding.btnUploadAudio.setOnClickListener {
            pickAudioLauncher.launch("audio/*")
        }

        // Upload new file from ready container
        binding.ibUploadNew.setOnClickListener {
            pickAudioLauncher.launch("audio/*")
        }

        // Reset clip button
        binding.ibResetRefAudio.setOnClickListener {
            loadDefaultAssetReference()
        }

        // Reference Audio Preview
        binding.btnPlayRefAudio.setOnClickListener {
            toggleReferenceAudioPreview()
        }
    }

    private fun setupStep3TargetAndLanguage() {
        binding.btnQuickIdeas.setOnClickListener {
            Toast.makeText(this, "Quick Ideas modal will be integrated in Phase 3", Toast.LENGTH_SHORT).show()
        }

        binding.btnClearTargetText.setOnClickListener {
            binding.etTargetText.setText("")
            updateValidationState()
        }

        binding.btnQuickEn.setOnClickListener {
            binding.etTargetText.setText("Google LiteRT is fast and clear.")
            updateValidationState()
        }
        binding.btnQuickHi.setOnClickListener {
            binding.etTargetText.setText("यह एक वॉइस क्लोनिंग का परीक्षण है।")
            updateValidationState()
        }
        binding.btnQuickTe.setOnClickListener {
            binding.etTargetText.setText("ఇది గూగుల్ లైట్-ఆర్టీతో వాయిస్ క్లోనింగ్ పరీక్ష.")
            updateValidationState()
        }
        binding.btnQuickTa.setOnClickListener {
            binding.etTargetText.setText("கூகிள் லைட்-ஆர்டி தொழில்நுட்பம் மூலம் குரல் உருவாக்கம்.")
            updateValidationState()
        }

        binding.btnSynthesize.setOnClickListener {
            synthesizeCurrentText()
        }
    }

    private fun setupStep4Output() {
        binding.btnPlayLatest.setOnClickListener {
            lastGeneratedPcm?.let { samples ->
                lifecycleScope.launch {
                    audioPlayer.play(samples, 24000)
                }
            }
        }

        binding.btnExportLatest.setOnClickListener {
            Toast.makeText(this, "Audio saved to app files: generated_voice.wav", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupValidationListeners() {
        binding.etRefText.addTextChangedListener { updateValidationState() }
        binding.etTargetText.addTextChangedListener { updateValidationState() }
    }

    private fun updateValidationState() {
        val hasRefAudio = refPcm != null
        val hasRefText = binding.etRefText.text.toString().trim().isNotEmpty()
        val hasTargetText = binding.etTargetText.text.toString().trim().isNotEmpty()

        if (!hasRefAudio) {
            binding.tvValidationHint.text = "⚠️ Step 2 reference audio required before generating."
            binding.btnSynthesize.isEnabled = false
        } else if (!hasRefText) {
            binding.tvValidationHint.text = "⚠️ Step 1 reference transcript cannot be empty."
            binding.btnSynthesize.isEnabled = false
        } else if (!hasTargetText) {
            binding.tvValidationHint.text = "💡 Enter target text above to generate speech."
            binding.btnSynthesize.isEnabled = false
        } else {
            binding.tvValidationHint.text = "💡 Ready to synthesize speech."
            binding.btnSynthesize.isEnabled = true
        }
    }

    private fun toggleRecording() {
        if (recorderHelper.isRecording) {
            stopLiveRecording()
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                startLiveRecording()
            } else {
                requestAudioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }
    }

    private fun startLiveRecording() {
        stopPreviewPlayer()
        val recordFile = File(cacheDir, "live_recorded_ref_${System.currentTimeMillis()}.wav")
        val success = recorderHelper.startRecording(recordFile)
        if (success) {
            binding.llRefAudioReady.visibility = View.GONE
            binding.llRefAudioNotReady.visibility = View.VISIBLE
            binding.llRecordingInProgress.visibility = View.VISIBLE
            binding.btnRecordAudio.text = "Stop Recording"
            binding.btnRecordAudio.setBackgroundColor(getColor(R.color.record_red))
            binding.btnUploadAudio.isEnabled = false
            binding.btnSynthesize.isEnabled = false
        } else {
            Toast.makeText(this, "Failed to start microphone recording", Toast.LENGTH_SHORT).show()
        }
    }

    private fun stopLiveRecording() {
        val recordedFile = recorderHelper.stopRecording()
        binding.llRecordingInProgress.visibility = View.GONE
        binding.btnRecordAudio.text = "Record Audio"
        binding.btnRecordAudio.setBackgroundColor(getColor(R.color.primary))
        binding.btnUploadAudio.isEnabled = true

        if (recordedFile != null && recordedFile.exists() && recordedFile.length() > 44) {
            val wavBytes = recordedFile.readBytes()
            val pcm = LiteRTIndicEngine.decodeWav(wavBytes)
            if (pcm != null && pcm.isNotEmpty()) {
                refPcm = pcm
                refAudioPath = recordedFile.absolutePath
                refAudioName = "recording.wav"

                val durationSec = pcm.size.toFloat() / 24000f
                binding.tvRefFileName.text = "Clip Ready ($refAudioName • ${String.format("%.2f", durationSec)}s)"
                binding.llRefAudioReady.visibility = View.VISIBLE
                binding.llRefAudioNotReady.visibility = View.GONE
                updateValidationState()
                Toast.makeText(this, "Voice recording ready!", Toast.LENGTH_SHORT).show()
                return
            }
        }
        Toast.makeText(this, "Recording too short or corrupted, please retry", Toast.LENGTH_SHORT).show()
        updateValidationState()
    }

    private fun handlePickedAudioUri(uri: Uri) {
        stopPreviewPlayer()
        try {
            val inputStream = contentResolver.openInputStream(uri) ?: return
            val tempFile = File(cacheDir, "uploaded_ref_${System.currentTimeMillis()}.wav")
            FileOutputStream(tempFile).use { out ->
                inputStream.copyTo(out)
            }
            inputStream.close()

            val wavBytes = tempFile.readBytes()
            // Check RIFF header
            val isRiff = wavBytes.size >= 12 &&
                    wavBytes[0] == 'R'.code.toByte() &&
                    wavBytes[1] == 'I'.code.toByte() &&
                    wavBytes[2] == 'F'.code.toByte() &&
                    wavBytes[3] == 'F'.code.toByte()

            if (!isRiff) {
                Toast.makeText(this, "Selected file is not a valid RIFF WAV audio file", Toast.LENGTH_LONG).show()
                return
            }

            val pcm = LiteRTIndicEngine.decodeWav(wavBytes)
            if (pcm == null || pcm.isEmpty()) {
                Toast.makeText(this, "Could not decode audio samples from file", Toast.LENGTH_SHORT).show()
                return
            }

            refPcm = pcm
            refAudioPath = tempFile.absolutePath
            refAudioName = getFileNameFromUri(uri) ?: "uploaded.wav"

            val durationSec = pcm.size.toFloat() / 24000f
            binding.tvRefFileName.text = "Clip Ready ($refAudioName • ${String.format("%.2f", durationSec)}s)"
            binding.llRefAudioReady.visibility = View.VISIBLE
            binding.llRefAudioNotReady.visibility = View.GONE
            updateValidationState()
            Toast.makeText(this, "Audio file uploaded successfully", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Error uploading audio: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun getFileNameFromUri(uri: Uri): String? {
        var name: String? = null
        val cursor = contentResolver.query(uri, null, null, null, null)
        cursor?.use {
            if (it.moveToFirst()) {
                val index = it.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                if (index != -1) name = it.getString(index)
            }
        }
        return name
    }

    private fun toggleReferenceAudioPreview() {
        if (isPreviewPlaying) {
            stopPreviewPlayer()
            binding.btnPlayRefAudio.text = "Preview"
            binding.btnPlayRefAudio.setIconResource(android.R.drawable.ic_media_play)
            binding.tvRefAudioStatus.text = "Tap to listen to reference audio"
        } else {
            val path = refAudioPath
            if (path == null) {
                // Play from raw PCM if loaded from asset
                refPcm?.let { pcm ->
                    lifecycleScope.launch {
                        binding.btnPlayRefAudio.text = "Stop"
                        binding.btnPlayRefAudio.setIconResource(android.R.drawable.ic_media_pause)
                        binding.tvRefAudioStatus.text = "Playing reference voice..."
                        isPreviewPlaying = true
                        audioPlayer.play(pcm, 24000)
                        binding.btnPlayRefAudio.text = "Preview"
                        binding.btnPlayRefAudio.setIconResource(android.R.drawable.ic_media_play)
                        binding.tvRefAudioStatus.text = "Preview finished"
                        isPreviewPlaying = false
                    }
                }
                return
            }

            try {
                previewMediaPlayer?.release()
                previewMediaPlayer = MediaPlayer().apply {
                    setDataSource(path)
                    prepare()
                    setOnCompletionListener {
                        binding.btnPlayRefAudio.text = "Preview"
                        binding.btnPlayRefAudio.setIconResource(android.R.drawable.ic_media_play)
                        binding.tvRefAudioStatus.text = "Preview finished"
                        isPreviewPlaying = false
                    }
                    start()
                }
                isPreviewPlaying = true
                binding.btnPlayRefAudio.text = "Stop"
                binding.btnPlayRefAudio.setIconResource(android.R.drawable.ic_media_pause)
                binding.tvRefAudioStatus.text = "Playing reference audio..."
            } catch (e: Exception) {
                Toast.makeText(this, "Preview failed: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun stopPreviewPlayer() {
        try {
            if (previewMediaPlayer?.isPlaying == true) {
                previewMediaPlayer?.stop()
            }
            previewMediaPlayer?.release()
            previewMediaPlayer = null
        } catch (ignored: Exception) {}
        isPreviewPlaying = false
    }

    private fun loadDefaultAssetReference() {
        stopPreviewPlayer()
        lifecycleScope.launch {
            try {
                val wavBytes = withContext(Dispatchers.IO) {
                    assets.open("samples/ref_en.wav").use { it.readBytes() }
                }
                refPcm = LiteRTIndicEngine.decodeWav(wavBytes)
                val defaultFile = File(cacheDir, "default_ref_en.wav")
                withContext(Dispatchers.IO) {
                    defaultFile.writeBytes(wavBytes)
                }
                refAudioPath = defaultFile.absolutePath
                refAudioName = "ref_en.wav"

                val durationSec = (refPcm?.size ?: 0).toFloat() / 24000f
                binding.tvRefFileName.text = "Clip Ready ($refAudioName • ${String.format("%.2f", durationSec)}s)"
                binding.llRefAudioReady.visibility = View.VISIBLE
                binding.llRefAudioNotReady.visibility = View.GONE
                updateValidationState()
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Failed to load default reference", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun initializeEngineAndDefaultReference() {
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

                loadDefaultAssetReference()

                val vmrss = TelemetryMonitor.getResidentMemoryMB()
                binding.tvMemoryInfo.text = "Resident Memory (VmRSS): $vmrss MB / 600 MB Target"
                binding.tvLatencyInfo.text = "Engine Ready. Tap Synthesize."
                updateValidationState()
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

                // Update Telemetry Diagnostics card
                binding.tvMemoryInfo.text = "Resident Memory (VmRSS): $vmrss MB / 600 MB Target"
                binding.tvLatencyInfo.text = "Mel: ${result.melTimeMs.toInt()}ms | DiT: ${result.diffusionTimeMs.toInt()}ms | Vocos: ${result.vocosTimeMs.toInt()}ms | Total: ${result.totalTimeMs.toInt()}ms"
                binding.tvRtfInfo.text = "Real-Time Factor: ${String.format("%.2f", result.realTimeFactor)}x (${String.format("%.2f", result.audioDurationSec)}s audio)"

                // Update Step 4 LATEST Card
                binding.llEmptyOutput.visibility = View.GONE
                binding.llLatestOutput.visibility = View.VISIBLE
                binding.tvLatestRtf.text = "RTF: ${String.format("%.2f", result.realTimeFactor)}x"
                binding.tvLatestRss.text = "Memory: $vmrss MB"
                binding.tvLatestTitle.text = "generated_voice_${System.currentTimeMillis()}.wav"

                // Save WAV
                try {
                    val wavFile = File(filesDir, "generated_voice.wav")
                    savePcmToWav(wavFile, result.audioSamples, 24000)
                } catch (ignored: Exception) {}

                // Auto-play generated audio
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

    private fun savePcmToWav(file: File, pcm: FloatArray, sampleRate: Int) {
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
        stopPreviewPlayer()
        audioPlayer.stop()
        if (recorderHelper.isRecording) {
            recorderHelper.stopRecording()
        }
    }
}
