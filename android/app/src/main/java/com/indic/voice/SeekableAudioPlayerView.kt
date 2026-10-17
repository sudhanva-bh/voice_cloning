package com.indic.voice

import android.content.Context
import android.media.MediaPlayer
import android.os.Handler
import android.os.Looper
import android.util.AttributeSet
import android.util.Log
import android.widget.FrameLayout
import android.widget.ImageButton
import android.widget.SeekBar
import android.widget.TextView
import java.io.File

class SeekableAudioPlayerView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    companion object {
        private const val TAG = "SeekablePlayer"
        private const val POLL_INTERVAL_MS = 30L
    }

    private val btnToggle: ImageButton
    private val seekBar: SeekBar
    private val tvTime: TextView

    private var mediaPlayer: MediaPlayer? = null
    private var currentPath: String? = null
    private var isUserScrubbing = false
    private var audioDurationMs = 0

    private val handler = Handler(Looper.getMainLooper())
    private val updateProgressRunnable = object : Runnable {
        override fun run() {
            val mp = mediaPlayer
            if (mp != null && mp.isPlaying && !isUserScrubbing) {
                val current = mp.currentPosition
                if (audioDurationMs > 0) {
                    val progress = (current.toFloat() / audioDurationMs * seekBar.max).toInt()
                    seekBar.progress = progress
                }
                tvTime.text = "${formatDuration(current)} / ${formatDuration(audioDurationMs)}"
                handler.postDelayed(this, POLL_INTERVAL_MS)
            }
        }
    }

    init {
        inflate(context, R.layout.view_seekable_audio_player, this)
        btnToggle = findViewById(R.id.btnPlayerToggle)
        seekBar = findViewById(R.id.sbPlayerProgress)
        tvTime = findViewById(R.id.tvPlayerTime)

        btnToggle.setOnClickListener {
            togglePlayPause()
        }

        seekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, progress: Int, fromUser: Boolean) {
                if (fromUser && audioDurationMs > 0) {
                    val targetMs = (progress.toFloat() / seekBar.max * audioDurationMs).toInt()
                    tvTime.text = "${formatDuration(targetMs)} / ${formatDuration(audioDurationMs)}"
                }
            }

            override fun onStartTrackingTouch(sb: SeekBar?) {
                isUserScrubbing = true
            }

            override fun onStopTrackingTouch(sb: SeekBar?) {
                isUserScrubbing = false
                val mp = mediaPlayer
                if (sb != null && mp != null && audioDurationMs > 0) {
                    val targetMs = (sb.progress.toFloat() / sb.max * audioDurationMs).toInt()
                    mp.seekTo(targetMs)
                }
            }
        })
    }

    fun setAudioPath(path: String?) {
        if (path == null) {
            resetPlayer()
            return
        }

        if (currentPath == path && mediaPlayer != null) {
            return
        }

        currentPath = path
        resetPlayer()

        try {
            val file = File(path)
            if (!file.exists()) {
                Log.w(TAG, "Audio file does not exist: $path")
                return
            }

            mediaPlayer = MediaPlayer().apply {
                setDataSource(path)
                prepare()
                audioDurationMs = duration
                setOnCompletionListener {
                    btnToggle.setImageResource(android.R.drawable.ic_media_play)
                    seekBar.progress = 0
                    tvTime.text = "00:00 / ${formatDuration(audioDurationMs)}"
                    handler.removeCallbacks(updateProgressRunnable)
                }
            }

            tvTime.text = "00:00 / ${formatDuration(audioDurationMs)}"
            seekBar.progress = 0
            btnToggle.isEnabled = true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load audio in player: ${e.message}", e)
            btnToggle.isEnabled = false
            tvTime.text = "--:-- / --:--"
        }
    }

    fun togglePlayPause() {
        val mp = mediaPlayer ?: return
        if (mp.isPlaying) {
            pause()
        } else {
            play()
        }
    }

    fun play() {
        val mp = mediaPlayer ?: return
        try {
            mp.start()
            btnToggle.setImageResource(android.R.drawable.ic_media_pause)
            handler.removeCallbacks(updateProgressRunnable)
            handler.post(updateProgressRunnable)
        } catch (e: Exception) {
            Log.e(TAG, "Error playing audio: ${e.message}")
        }
    }

    fun pause() {
        val mp = mediaPlayer ?: return
        try {
            if (mp.isPlaying) {
                mp.pause()
            }
            btnToggle.setImageResource(android.R.drawable.ic_media_play)
            handler.removeCallbacks(updateProgressRunnable)
        } catch (e: Exception) {
            Log.e(TAG, "Error pausing audio: ${e.message}")
        }
    }

    fun stop() {
        pause()
        mediaPlayer?.seekTo(0)
        seekBar.progress = 0
        if (audioDurationMs > 0) {
            tvTime.text = "00:00 / ${formatDuration(audioDurationMs)}"
        }
    }

    fun resetPlayer() {
        handler.removeCallbacks(updateProgressRunnable)
        try {
            mediaPlayer?.stop()
            mediaPlayer?.release()
        } catch (ignored: Exception) {}
        mediaPlayer = null
        audioDurationMs = 0
        btnToggle.setImageResource(android.R.drawable.ic_media_play)
        seekBar.progress = 0
        tvTime.text = "00:00 / 00:00"
    }

    fun release() {
        resetPlayer()
        currentPath = null
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        release()
    }

    private fun formatDuration(durationMs: Int): String {
        val totalSec = durationMs / 1000
        val min = totalSec / 60
        val sec = totalSec % 60
        return String.format("%02d:%02d", min, sec)
    }
}
