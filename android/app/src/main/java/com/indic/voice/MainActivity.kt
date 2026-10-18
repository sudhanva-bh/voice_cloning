package com.indic.voice

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.core.widget.addTextChangedListener
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.snackbar.Snackbar
import com.indic.voice.databinding.ActivityMainBinding
import com.indic.voice.audio.WaveformStitcher
import com.indic.voice.history.AudioExporter
import com.indic.voice.history.GeneratedClipItem
import com.indic.voice.history.GenerationHistoryManager
import com.indic.voice.history.HistoryAdapter
import com.indic.voice.presets.ExampleScriptsBottomSheet
import com.indic.voice.presets.QuickIdeasBottomSheet
import com.indic.voice.text.MultilingualChunker
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val engine by lazy { LiteRTIndicEngine(this) }
    private val recorderHelper by lazy { AudioRecorderHelper() }
    private val historyManager by lazy { GenerationHistoryManager(this) }
    private val audioExporter by lazy { AudioExporter(this) }
    private val sessionCache by lazy { SessionCacheManager(this) }
    private val chunker by lazy { MultilingualChunker() }
    private val stitcher by lazy { WaveformStitcher() }

    private lateinit var historyAdapter: HistoryAdapter

    private var refPcm: FloatArray? = null
    private var refAudioPath: String? = null
    private var refAudioName: String = "ref_en.wav"
    private var latestGeneratedFile: File? = null
    private var synthesisJob: Job? = null

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
        setupStep4History()
        setupValidationListeners()

        loadSession()
        initializeEngine()
    }

    private fun setupStep1Listeners() {
        binding.btnClearRefText.setOnClickListener {
            binding.etRefText.setText("")
            sessionCache.refText = ""
            updateValidationState()
        }

        binding.btnExampleScripts.setOnClickListener {
            ExampleScriptsBottomSheet { script ->
                binding.etRefText.setText(script)
                sessionCache.refText = script
                updateValidationState()
                showFeedback("Reference script updated!")
            }.show(supportFragmentManager, "ExampleScriptsBottomSheet")
        }
    }

    private fun setupStep2RecordingAndPicker() {
        // Record audio button
        binding.btnRecordAudio.setOnClickListener {
            toggleRecording()
        }

        // Re-record button inside ready state
        binding.btnReRecordAudio.setOnClickListener {
            binding.playerRefAudio.pause()
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
            sessionCache.clearReference()
            loadDefaultAssetReference()
        }
    }

    private fun setupStep3TargetAndLanguage() {
        binding.btnQuickIdeas.setOnClickListener {
            QuickIdeasBottomSheet { idea ->
                binding.etTargetText.setText(idea)
                sessionCache.targetText = idea
                updateValidationState()
                showFeedback("Target speech updated!")
            }.show(supportFragmentManager, "QuickIdeasBottomSheet")
        }

        binding.btnClearTargetText.setOnClickListener {
            binding.etTargetText.setText("")
            sessionCache.targetText = ""
            updateValidationState()
        }


        binding.rgSteps.setOnCheckedChangeListener { _, checkedId ->
            val steps = when (checkedId) {
                binding.rbStep8.id -> 8
                binding.rbStep24.id -> 24
                else -> 16
            }
            sessionCache.cfmSteps = steps
        }

        binding.btnSynthesize.setOnClickListener {
            synthesizeCurrentText()
        }

        binding.btnCancelSynthesis.setOnClickListener {
            synthesisJob?.cancel()
        }
    }

    private fun setupStep4History() {
        historyAdapter = HistoryAdapter(
            onExport = { clipItem ->
                exportClipToDownloads(clipItem.file, clipItem.displayTitle)
            },
            onShare = { clipItem ->
                shareAudioClip(clipItem.file, clipItem.displayTitle)
            },
            onDelete = { clipItem ->
                deleteClipFromHistory(clipItem)
            }
        )

        binding.rvGenerationHistory.layoutManager = LinearLayoutManager(this)
        binding.rvGenerationHistory.adapter = historyAdapter

        binding.btnShareLatest.setOnClickListener {
            latestGeneratedFile?.let { file ->
                val title = binding.tvLatestTitle.text.toString()
                shareAudioClip(file, title)
            }
        }

        binding.btnExportLatest.setOnClickListener {
            latestGeneratedFile?.let { file ->
                val title = binding.tvLatestTitle.text.toString()
                exportClipToDownloads(file, title)
            }
        }

        refreshHistoryList()
    }

    private fun setupValidationListeners() {
        binding.etRefText.addTextChangedListener {
            sessionCache.refText = it?.toString() ?: ""
            updateValidationState()
        }
        binding.etTargetText.addTextChangedListener {
            sessionCache.targetText = it?.toString() ?: ""
            updateValidationState()
        }
    }

    private fun loadSession() {
        binding.etRefText.setText(sessionCache.refText)
        binding.etTargetText.setText(sessionCache.targetText)

        when (sessionCache.cfmSteps) {
            8 -> binding.rbStep8.isChecked = true
            24 -> binding.rbStep24.isChecked = true
            else -> binding.rbStep16.isChecked = true
        }

        val cachedPath = sessionCache.refClipPath
        val cachedName = sessionCache.refFileName
        if (!cachedPath.isNullOrEmpty() && File(cachedPath).exists()) {
            val file = File(cachedPath)
            val pcm = LiteRTIndicEngine.decodeWav(file.readBytes())
            if (pcm != null && pcm.isNotEmpty()) {
                refPcm = pcm
                refAudioPath = cachedPath
                refAudioName = cachedName ?: file.name

                val durationSec = pcm.size.toFloat() / 24000f
                binding.tvRefFileName.text = "Clip Ready ($refAudioName • ${String.format("%.2f", durationSec)}s)"
                binding.playerRefAudio.setAudioPath(refAudioPath)
                binding.llRefAudioReady.visibility = View.VISIBLE
                binding.llRefAudioNotReady.visibility = View.GONE
                updateValidationState()
                return
            }
        }
        loadDefaultAssetReference()
    }

    private fun refreshHistoryList() {
        val history = historyManager.loadHistory()
        if (history.isEmpty()) {
            binding.llEmptyOutput.visibility = View.VISIBLE
            binding.llLatestOutput.visibility = View.GONE
            binding.llHistorySection.visibility = View.GONE
            latestGeneratedFile = null
        } else {
            binding.llEmptyOutput.visibility = View.GONE
            binding.llLatestOutput.visibility = View.VISIBLE

            val latest = history.first()
            latestGeneratedFile = latest.file
            binding.tvLatestTitle.text = latest.displayTitle

            if (!latest.rtf.isNullOrEmpty()) {
                binding.tvLatestRtf.visibility = View.VISIBLE
                binding.tvLatestRtf.text = "RTF: ${latest.rtf}x"
            } else {
                binding.tvLatestRtf.visibility = View.GONE
            }

            if (!latest.rssMB.isNullOrEmpty()) {
                binding.tvLatestRss.visibility = View.VISIBLE
                binding.tvLatestRss.text = "Memory: ${latest.rssMB} MB"
            } else {
                binding.tvLatestRss.visibility = View.GONE
            }

            binding.playerLatestAudio.setAudioPath(latest.file.absolutePath)

            // Past generations (skip 1)
            if (history.size > 1) {
                val pastClips = history.drop(1)
                binding.llHistorySection.visibility = View.VISIBLE
                binding.tvHistoryHeader.text = "Previous Generations (${pastClips.size}):"
                historyAdapter.setItems(pastClips)
            } else {
                binding.llHistorySection.visibility = View.GONE
            }
        }
    }

    private fun exportClipToDownloads(file: File, displayTitle: String) {
        val exportResult = audioExporter.exportToDownloads(file, displayTitle)
        if (exportResult != null) {
            Snackbar.make(binding.root, "Saved to Downloads: $exportResult", Snackbar.LENGTH_LONG)
                .setBackgroundTint(getColor(R.color.card_dark))
                .setTextColor(getColor(R.color.accent_green))
                .show()
        } else {
            Toast.makeText(this, "Failed to export audio to Downloads", Toast.LENGTH_SHORT).show()
        }
    }

    private fun shareAudioClip(file: File, displayTitle: String) {
        if (!file.exists()) {
            Toast.makeText(this, "Audio file not found", Toast.LENGTH_SHORT).show()
            return
        }
        try {
            val uri = FileProvider.getUriForFile(
                this,
                "${applicationContext.packageName}.fileprovider",
                file
            )
            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "audio/wav"
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_SUBJECT, displayTitle)
                putExtra(Intent.EXTRA_TEXT, "Voice cloned with Indic LiteRT Voice Cloning")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(shareIntent, "Share Audio Clip"))
        } catch (e: Exception) {
            Log.e("MainActivity", "Failed to share audio clip", e)
            Toast.makeText(this, "Failed to share: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun deleteClipFromHistory(item: GeneratedClipItem) {
        historyManager.deleteClip(item.file)
        refreshHistoryList()
        Snackbar.make(binding.root, "Deleted clip: ${item.displayTitle}", Snackbar.LENGTH_SHORT)
            .setBackgroundTint(getColor(R.color.card_dark))
            .setTextColor(getColor(R.color.text_primary))
            .show()
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
        binding.playerRefAudio.pause()
        binding.playerLatestAudio.pause()
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

                sessionCache.refClipPath = refAudioPath
                sessionCache.refFileName = refAudioName

                val durationSec = pcm.size.toFloat() / 24000f
                binding.tvRefFileName.text = "Clip Ready ($refAudioName • ${String.format("%.2f", durationSec)}s)"
                binding.playerRefAudio.setAudioPath(refAudioPath)
                binding.llRefAudioReady.visibility = View.VISIBLE
                binding.llRefAudioNotReady.visibility = View.GONE
                updateValidationState()
                showFeedback("Voice recording ready!")
                return
            }
        }
        Toast.makeText(this, "Recording too short or corrupted, please retry", Toast.LENGTH_SHORT).show()
        updateValidationState()
    }

    private fun handlePickedAudioUri(uri: Uri) {
        binding.playerRefAudio.pause()
        try {
            val inputStream = contentResolver.openInputStream(uri) ?: return
            val tempFile = File(cacheDir, "uploaded_ref_${System.currentTimeMillis()}.wav")
            FileOutputStream(tempFile).use { out ->
                inputStream.copyTo(out)
            }
            inputStream.close()

            val wavBytes = tempFile.readBytes()
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

            sessionCache.refClipPath = refAudioPath
            sessionCache.refFileName = refAudioName

            val durationSec = pcm.size.toFloat() / 24000f
            binding.tvRefFileName.text = "Clip Ready ($refAudioName • ${String.format("%.2f", durationSec)}s)"
            binding.playerRefAudio.setAudioPath(refAudioPath)
            binding.llRefAudioReady.visibility = View.VISIBLE
            binding.llRefAudioNotReady.visibility = View.GONE
            updateValidationState()
            showFeedback("Audio file uploaded successfully!")
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

    private fun loadDefaultAssetReference() {
        binding.playerRefAudio.pause()
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
                binding.playerRefAudio.setAudioPath(refAudioPath)
                binding.llRefAudioReady.visibility = View.VISIBLE
                binding.llRefAudioNotReady.visibility = View.GONE
                updateValidationState()
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Failed to load default reference", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun initializeEngine() {
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

        // 1. Segment text into safe chunks that obey the 512-frame window
        val chunks = chunker.split(targetText)
        if (chunks.isEmpty()) {
            Toast.makeText(this, "No valid text to synthesize", Toast.LENGTH_SHORT).show()
            return
        }

        val steps = when (binding.rgSteps.checkedRadioButtonId) {
            binding.rbStep8.id -> 8
            binding.rbStep24.id -> 24
            else -> 16
        }

        binding.playerRefAudio.pause()
        binding.playerLatestAudio.pause()

        // Configure UI for progress
        binding.btnSynthesize.visibility = View.GONE
        binding.llSynthesisProgress.visibility = View.VISIBLE
        binding.btnCancelSynthesis.isEnabled = true

        if (chunks.size == 1) {
            binding.chunkProgressBar.isIndeterminate = true
            binding.tvChunkProgressTitle.text = "Synthesizing voice (1 chunk)..."
            binding.tvChunkSubText.text = chunks[0].text
        } else {
            binding.chunkProgressBar.isIndeterminate = false
            binding.chunkProgressBar.max = chunks.size
            binding.chunkProgressBar.progress = 0
            binding.tvChunkProgressTitle.text = "Synthesizing sentence 1 of ${chunks.size}..."
            binding.tvChunkSubText.text = chunks[0].text
        }

        binding.tvLatencyInfo.text = "Solving Flow Matching ODE ($steps steps, ${chunks.size} chunk${if (chunks.size > 1) "s" else ""})..."

        synthesisJob = lifecycleScope.launch {
            val chunkWaveforms = mutableListOf<FloatArray>()
            var totalDiffMs = 0f
            var totalVocMs = 0f
            var totalIstftMs = 0f
            var totalComputeMs = 0f
            var isCancelled = false

            try {
                // Precompute speaker conditioning Mel ONCE
                val refOk = engine.setReferenceAudio(pcm, refText)
                if (!refOk) {
                    throw IllegalStateException("Failed to extract reference audio Mel conditioning")
                }

                // Sequential synthesis loop
                for (chunk in chunks) {
                    if (!isActive) {
                        isCancelled = true
                        break
                    }

                    withContext(Dispatchers.Main) {
                        binding.chunkProgressBar.progress = chunk.index
                        binding.tvChunkProgressTitle.text = "Synthesizing sentence ${chunk.index + 1} of ${chunks.size}..."
                        binding.tvChunkSubText.text = chunk.text
                    }

                    val chunkRes = engine.synthesizeChunk(
                        chunkText = chunk.text,
                        numSteps = steps,
                        cfgStrength = 2.0f,
                        seed = 42 + chunk.index
                    )

                    if (!isActive) {
                        isCancelled = true
                        break
                    }

                    if (chunkRes.audioSamples.isNotEmpty()) {
                        chunkWaveforms.add(chunkRes.audioSamples)
                    }

                    totalDiffMs += chunkRes.diffusionTimeMs
                    totalVocMs += chunkRes.vocosTimeMs
                    totalIstftMs += chunkRes.istftTimeMs
                    totalComputeMs += chunkRes.totalTimeMs
                }

                if (isCancelled || !isActive) {
                    showFeedback("Synthesis cancelled.")
                    return@launch
                }

                if (chunkWaveforms.isEmpty()) {
                    Toast.makeText(this@MainActivity, "Synthesis produced no audio", Toast.LENGTH_SHORT).show()
                    return@launch
                }

                // Stitch audio chunks with 5ms cosine crossfade and 120ms natural pauses
                val finalWaveform = withContext(Dispatchers.Default) {
                    stitcher.stitch(chunkWaveforms)
                }

                val finalDurationSec = finalWaveform.size.toFloat() / 24000f
                val finalRtf = (totalComputeMs / 1000f) / maxOf(finalDurationSec, 0.01f)
                val vmrss = TelemetryMonitor.getResidentMemoryMB()

                // Update Telemetry Diagnostics card
                binding.tvMemoryInfo.text = "Resident Memory (VmRSS): $vmrss MB / 600 MB Target"
                binding.tvLatencyInfo.text = "Chunks: ${chunks.size} | DiT: ${totalDiffMs.toInt()}ms | Vocos: ${totalVocMs.toInt()}ms | Total: ${totalComputeMs.toInt()}ms"
                binding.tvRtfInfo.text = "Real-Time Factor: ${String.format("%.2f", finalRtf)}x (${String.format("%.2f", finalDurationSec)}s audio across ${chunks.size} chunks)"

                // Save stitched WAV into persistent Generation History
                val clipFile = withContext(Dispatchers.IO) {
                    historyManager.saveGeneratedClip(finalWaveform, finalRtf, vmrss)
                }

                // Refresh history list and auto-play latest
                refreshHistoryList()
                binding.playerLatestAudio.play()

                showFeedback("Generated ${String.format("%.1f", finalDurationSec)}s audio across ${chunks.size} sentences!")

            } catch (e: kotlinx.coroutines.CancellationException) {
                showFeedback("Synthesis cancelled.")
            } catch (e: Exception) {
                binding.tvLatencyInfo.text = "Synthesis Error: ${e.localizedMessage}"
                Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                binding.btnSynthesize.visibility = View.VISIBLE
                binding.btnSynthesize.isEnabled = true
                binding.llSynthesisProgress.visibility = View.GONE
                synthesisJob = null
            }
        }
    }

    private fun showFeedback(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_SHORT)
            .setBackgroundTint(getColor(R.color.card_dark))
            .setTextColor(getColor(R.color.text_primary))
            .show()
    }

    override fun onDestroy() {
        super.onDestroy()
        binding.playerRefAudio.release()
        binding.playerLatestAudio.release()
        if (recorderHelper.isRecording) {
            recorderHelper.stopRecording()
        }
    }
}
