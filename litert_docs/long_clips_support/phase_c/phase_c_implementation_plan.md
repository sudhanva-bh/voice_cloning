# Phase C Implementation Plan: Waveform Stitching & Acoustic Audio Pipeline

**Module**: `android/app` (Kotlin)  
**Parent Plan**: [long_clips_implementation_plan.md](file:///c:/voice_cloning/litert_docs/long_clips_support/long_clips_implementation_plan.md)  
**Goal**: Design, implement, and unit-test a high-fidelity `WaveformStitcher` module that concatenates sequential speech chunks into a single, cohesive, publication-quality audio waveform with natural human-like cadence, zero boundary pops, and calibrated peak normalization.

---

## 1. Acoustic Challenges & Mathematical Solutions

When concatenating independently synthesized neural TTS chunks, naive array concatenation causes two noticeable acoustic defects:
1. **Boundary Spectral Splatter & Clicking**: If chunk $i$ ends on an arbitrary non-zero sample value and chunk $i+1$ begins on a non-zero sample, the abrupt step function causes high-frequency DC discontinuity clicks.
2. **Machine-Gun Cadence (Unnatural Pacing)**: Human speech naturally includes breathing pauses between sentences ($\approx 100\text{ms} - 250\text{ms}$). Zero silence between sentences sounds robotic and breathless.

### 1.1 Raised-Cosine Boundary Smoothing
To eliminate DC offset clicks without altering speech formant characteristics, we apply a 5ms **Raised-Cosine (Hann) Window** at chunk boundaries ($L = 120\text{ samples}$ at 24 kHz):

$$\text{Fade-Out: } w_{\text{out}}[k] = \frac{1}{2} \left(1 + \cos\left(\frac{\pi k}{L}\right)\right), \quad k \in [0, L-1]$$
$$\text{Fade-In: } w_{\text{in}}[k] = \frac{1}{2} \left(1 - \cos\left(\frac{\pi k}{L}\right)\right), \quad k \in [0, L-1]$$

Because $\frac{dw}{dk} = 0$ at both $k=0$ and $k=L$, the transition has continuous first derivatives and generates **0 dB spectral splatter**.

### 1.2 Inter-Sentence Natural Silence Pause
We insert **120ms of silence** between sentence chunks:
$$\text{Silence Samples} = 0.120\text{s} \times 24,000\text{ Hz} = 2,880 \text{ samples}$$

### 1.3 Global Dynamic Peak Normalization
Individual chunks may have slightly varying gain levels. Once all chunks are stitched:
$$\text{Scale} = \frac{0.95}{\max_{n} |x[n]| + \epsilon}$$
All samples are scaled so the master waveform peaks at $-0.45\text{ dBFS}$ ($0.95$), preventing digital clipping in Android `AudioTrack` or downstream Bluetooth DACs.

---

## 2. API & Data Structure Specification

```kotlin
package com.indic.voice.audio

class WaveformStitcher(
    val sampleRate: Int = 24000,
    val interSentenceSilenceMs: Int = 120,
    val fadeDurationMs: Float = 5.0f,
    val targetPeak: Float = 0.95f
) {
    /**
     * Stitches a list of PCM float arrays into a single continuous waveform.
     */
    fun stitch(chunks: List<FloatArray>): FloatArray

    /**
     * Applies in-place raised-cosine fade-in and fade-out to an individual chunk.
     */
    fun applyBoundaryFades(samples: FloatArray)
}
```

---

## 3. Work Breakdown & Implementation Steps

1. **Create `WaveformStitcher.kt`**:
   - Package: `com.indic.voice.audio`
   - File: `android/app/src/main/java/com/indic/voice/audio/WaveformStitcher.kt`
   - Implement pre-allocated single-pass buffer stitching.
   - Implement raised-cosine fade ramps.
   - Implement 120ms silence padding and global peak normalization.

2. **Create Unit Tests (`WaveformStitcherTest.kt`)**:
   - File: `android/app/src/test/java/com/indic/voice/audio/WaveformStitcherTest.kt`
   - Test cases:
     * Empty input list handling.
     * Single chunk pass-through with fade ramps and peak scaling.
     * Multi-chunk concatenation length verification ($\sum \text{len}_i + (N-1) \times 2880$).
     * Silence insertion verification (verify middle segment contains exact zeros).
     * Boundary smoothing verification (first sample $\approx 0$, boundary transition $\approx 0$).
     * Peak normalization guarantee ($\max |x[n]| \le 0.951$).
     * Performance benchmark ($< 5\text{ms}$ execution for 30s audio).

3. **Compilation & Test Verification**:
   - Run `gradlew testDebugUnitTest` in `android/`.
   - Run `gradlew assembleDebug` in `android/`.

4. **Execution Report**:
   - Document results in `litert_docs/long_clips_support/phase_c/phase_c_execution_report.md`.
