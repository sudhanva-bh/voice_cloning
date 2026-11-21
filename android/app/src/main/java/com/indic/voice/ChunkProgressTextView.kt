package com.indic.voice

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Path
import android.util.AttributeSet
import android.view.animation.LinearInterpolator
import androidx.appcompat.widget.AppCompatTextView
import androidx.core.content.ContextCompat

class ChunkProgressTextView(context: Context, attrs: AttributeSet?) : AppCompatTextView(context, attrs) {
    private val highlightColor = ContextCompat.getColor(context, R.color.secondary)
    private val highlightPath = Path()
    private var progress = 0f
    private var progressAnimator: ValueAnimator? = null
    private var chunkAnimator: ValueAnimator? = null
    private var pendingProgress: Float? = null

    fun setChunk(chunk: CharSequence) {
        resetChunkTransition()
        setProgress(0f, animate = false)
        text = chunk
    }

    fun transitionToChunk(chunk: CharSequence, onShown: () -> Unit) {
        if (text.isEmpty() || !isLaidOut || !isShown || !ValueAnimator.areAnimatorsEnabled()) {
            setChunk(chunk)
            onShown()
            return
        }

        resetChunkTransition()
        pendingProgress = 0f
        val swapPoint = 0.4f
        val distance = 3f * resources.displayMetrics.density
        chunkAnimator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 260
            interpolator = LinearInterpolator()
            addUpdateListener { animation ->
                val position = animation.animatedFraction
                if (position < swapPoint) {
                    val fadeOut = position / swapPoint
                    alpha = 1f - fadeOut
                    translationY = -distance * fadeOut
                } else {
                    pendingProgress?.let { incomingProgress ->
                        pendingProgress = null
                        text = chunk
                        setProgress(0f, animate = false)
                        setProgress(incomingProgress)
                        onShown()
                    }
                    val fadeIn = (position - swapPoint) / (1f - swapPoint)
                    alpha = fadeIn
                    translationY = distance * (1f - fadeIn)
                }
            }
            start()
        }
    }

    fun setProgress(fraction: Float, animate: Boolean = true) {
        val target = fraction.coerceIn(0f, 1f)
        if (pendingProgress != null) {
            pendingProgress = target
            return
        }
        progressAnimator?.cancel()
        progressAnimator = null
        if (!animate || target == progress) {
            progress = target
            invalidate()
            return
        }

        progressAnimator = ValueAnimator.ofFloat(progress, target).apply {
            duration = 320
            interpolator = LinearInterpolator()
            addUpdateListener {
                progress = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val textLayout = layout ?: return
        if (progress <= 0f) return

        // Measure across the laid-out lines so wrapping and shaped glyphs stay intact.
        var textWidth = 0f
        for (line in 0 until textLayout.lineCount) {
            textWidth += textLayout.getLineRight(line) - textLayout.getLineLeft(line)
        }
        var highlightedWidth = textWidth * progress
        highlightPath.rewind()
        for (line in 0 until textLayout.lineCount) {
            if (highlightedWidth <= 0f) break
            val left = textLayout.getLineLeft(line)
            val right = textLayout.getLineRight(line)
            val lineWidth = right - left
            val fill = highlightedWidth.coerceAtMost(lineWidth)
            val top = textLayout.getLineTop(line).toFloat()
            val bottom = textLayout.getLineBottom(line).toFloat()
            val rtl = textLayout.getParagraphDirection(line) < 0
            highlightPath.addRect(
                if (rtl) right - fill else left,
                top,
                if (rtl) right else left + fill,
                bottom,
                Path.Direction.CW
            )
            highlightedWidth -= lineWidth
        }

        val save = canvas.save()
        canvas.translate(totalPaddingLeft.toFloat(), totalPaddingTop.toFloat())
        canvas.clipPath(highlightPath)
        val originalColor = textLayout.paint.color
        textLayout.paint.color = highlightColor
        textLayout.draw(canvas)
        textLayout.paint.color = originalColor
        canvas.restoreToCount(save)
    }

    override fun onDetachedFromWindow() {
        freezeProgress()
        super.onDetachedFromWindow()
    }

    fun freezeProgress() {
        resetChunkTransition()
        progressAnimator?.cancel()
        progressAnimator = null
    }

    private fun resetChunkTransition() {
        chunkAnimator?.cancel()
        chunkAnimator = null
        pendingProgress = null
        alpha = 1f
        translationY = 0f
    }
}
