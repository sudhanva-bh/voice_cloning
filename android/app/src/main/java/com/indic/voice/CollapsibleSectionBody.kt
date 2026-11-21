package com.indic.voice

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View
import android.view.animation.PathInterpolator
import android.widget.LinearLayout
import androidx.core.animation.doOnEnd
import kotlin.math.abs
import kotlin.math.roundToInt
import kotlin.math.roundToLong

class CollapsibleSectionBody(context: Context, attrs: AttributeSet?) : LinearLayout(context, attrs) {
    var isExpanded = true
        private set

    private var revealFraction = 1f
    private var animator: ValueAnimator? = null

    fun setExpanded(expanded: Boolean, chevron: View, animate: Boolean = true) {
        isExpanded = expanded
        animator?.removeAllListeners()
        animator?.cancel()
        animator = null

        val target = if (expanded) 1f else 0f
        fun settle() {
            updateReveal(target, chevron)
            visibility = if (expanded) VISIBLE else GONE
            importantForAccessibility = if (expanded) {
                IMPORTANT_FOR_ACCESSIBILITY_AUTO
            } else {
                IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS
            }
        }

        if (!animate || !isAttachedToWindow || !ValueAnimator.areAnimatorsEnabled() || revealFraction == target) {
            settle()
            return
        }

        visibility = VISIBLE
        importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS
        animator = ValueAnimator.ofFloat(revealFraction, target).apply {
            duration = (280f * abs(target - revealFraction)).roundToLong().coerceAtLeast(90)
            interpolator = PathInterpolator(0.2f, 0f, 0f, 1f)
            addUpdateListener { updateReveal(it.animatedValue as Float, chevron) }
            doOnEnd {
                animator = null
                settle()
            }
            start()
        }
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        if (revealFraction == 1f) {
            super.onMeasure(widthMeasureSpec, heightMeasureSpec)
            return
        }
        // Keep child measurements at their natural size and reveal them from the top.
        super.onMeasure(widthMeasureSpec, MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED))
        setMeasuredDimension(measuredWidthAndState, (measuredHeight * revealFraction).roundToInt())
    }

    override fun dispatchDraw(canvas: Canvas) {
        val save = canvas.save()
        canvas.clipRect(0, 0, width, height)
        super.dispatchDraw(canvas)
        canvas.restoreToCount(save)
    }

    override fun dispatchTouchEvent(event: MotionEvent): Boolean =
        (isExpanded && revealFraction == 1f) && super.dispatchTouchEvent(event)

    override fun onDetachedFromWindow() {
        animator?.end()
        super.onDetachedFromWindow()
    }

    private fun updateReveal(fraction: Float, chevron: View) {
        revealFraction = fraction
        alpha = fraction
        chevron.rotation = 180f * fraction
        requestLayout()
    }
}
