# Phase E Implementation Plan: Preset Expansion & Long Paragraph Support

**Module**: `android/app` (Kotlin)  
**Parent Plan**: [long_clips_implementation_plan.md](file:///c:/voice_cloning/litert_docs/long_clips_support/long_clips_implementation_plan.md)  
**Goal**: Expand `PresetModels.kt` and `QuickIdeasBottomSheet.kt` with realistic Short (1 sentence, ~2.5s), Medium (2–3 sentences, ~6–8s), and Long Paragraph (~15–20s) presets across all 4 supported languages (English, Hindi, Telugu, Tamil), verifying that the new multi-chunk orchestration engine synthesizes and stitches them with high fidelity on physical edge hardware (Samsung Galaxy S23).

---

## 1. Technical Rationale & Objectives

Now that Phases A through D are fully operational:
1. `MultilingualChunker` safely breaks long paragraphs into sequential sub-window chunks.
2. The C++ engine caches speaker conditioning Mel features and executes sequential chunk inference.
3. `WaveformStitcher` crossfades chunk boundaries and inserts 120ms natural inter-sentence pauses.
4. `MainActivity` provides a dynamic progress bar (`"Synthesizing sentence X of N"`), active cancellation, and aggregated telemetry.

We can now safely restore and expand rich multi-sentence and paragraph-length presets in the UI without risking DiT 512-frame window overflow or speech distortion.

---

## 2. Preset Library Structure (`PresetModels.kt`)

For each language (English, Hindi, Telugu, Tamil):
1. **Short (~2.5s, 1 chunk)**: Quick functional testing and latency verification.
2. **Medium (~6s–8s, 2 chunks)**: Compound sentences evaluating inter-sentence pause naturalness and boundary smoothing.
3. **Paragraph (~15s–20s, 3–4 chunks)**: Rich narrative paragraph evaluating multi-chunk sequential stability, steady VmRSS memory footprint, and cumulative audio stitching.

### 2.1 Badge Specification (`QuickIdeasBottomSheet.kt`)
* `IdeaSection.SHORT` $\to$ `"Short (~2.5s)"`
* `IdeaSection.MEDIUM` $\to$ `"Medium (~7s)"`
* `IdeaSection.LONG` $\to$ `"Paragraph (~15s)"`

---

## 3. Work Breakdown & Steps

1. **Update `PresetModels.kt`**:
   - Re-populate `PresetData.quickIdeas` with calibrated Short, Medium, and Long Paragraph entries for English, Hindi, Telugu, and Tamil.
2. **Update `QuickIdeasBottomSheet.kt`**:
   - Update length display badges to accurately indicate duration tiers.
3. **Compilation & Testing**:
   - Run `gradlew testDebugUnitTest` (all unit tests must pass).
   - Run `gradlew assembleDebug` (compile release-ready debug APK).
4. **Physical Device Installation**:
   - Deploy APK to Samsung Galaxy S23 via `adb install -r android/app/build/outputs/apk/debug/app-debug.apk`.
5. **Execution Report**:
   - Document results in `litert_docs/long_clips_support/phase_e/phase_e_execution_report.md`.
