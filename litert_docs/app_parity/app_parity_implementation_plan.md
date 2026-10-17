# IndicVoice Native UI Parity Implementation Plan
## Replicating Flutter VoiceCloneProto Feature Set on Android Native (LiteRT IndicF5)

**Document Version**: 1.0.0  
**Target Architecture**: Android Native (Kotlin + Material Design 3 + C++ JNI)  
**Target Hardware**: Samsung Galaxy S23 (Snapdragon 8 Gen 2 / SM-S911B) & Helio P22T  
**Core Model**: IndicF5-TTS INT8 with LiteRT / XNNPACK  

---

## 1. Executive Summary & Objective

The objective of this initiative is to elevate the native Android **IndicF5 LiteRT** application from its current engineering diagnostic harness to full UI, workflow, and feature parity with the prototype Flutter application (`voice_clone_proto`).

While the Flutter prototype relied on Sherpa-ONNX (ZipVoice) with heavy Dart Isolates and asset bundle extraction, the native Android implementation provides:
1. **Direct JNI Execution**: Zero Dart-to-C++ FFI marshalling overhead, driving the already verified LiteRT IndicF5 pipeline (0 NaNs, 21s total execution, RTF ~1.3x).
2. **Native Audio Capture**: Clean, low-latency 24 kHz 16-bit mono PCM recording using Android's `AudioRecord` API with instant WAV container generation.
3. **Native Media Playback**: Interactive seekable audio players with scrubbing, waveform/progress indicators, and state management.
4. **Export & History Storage**: Scoped-storage compliant audio export to the public `Download/` directory via Android's `MediaStore` API.

---

## 2. Feature & Architecture Comparison

| Feature Dimension | Flutter Prototype (`voice_clone_proto`) | Native Android IndicF5 (`android/`) |
| :--- | :--- | :--- |
| **Theme & Aesthetic** | Material 3 Dark (Seed: Deep Purple) | Material 3 Dark (`Theme.Material3.DayNight.NoActionBar` with tailored purple accents) |
| **Step 1: Reference Script** | Text input + Modal BottomSheet with 4 example transcripts | `TextInputLayout` + `TextInputEditText` + `BottomSheetDialogFragment` with example transcripts |
| **Step 2: Voice Audio** | Microphone recording (`record`) + File Picker (`file_picker`) + Inline player | Native `AudioRecord` (24kHz mono) + `ActivityResultContracts.GetContent` + `SeekableAudioPlayer` |
| **Step 3: Target Text** | Text input + Quick Ideas Modal (Short, Medium, Long) | `TextInputLayout` + Quick Ideas Modal + Multilingual Indic language quick-chips (Hindi, Tamil, Telugu, English) |
| **Sampling Parameters** | Fixed 4 ODE steps in ZipVoice | Configurable CFM Steps (8 Fast, 16 Balanced, 24 HQ) |
| **Step 4: Output & Library** | "LATEST" gradient card + Generation history list + Audio export | Highlighted gradient card + `RecyclerView` history + Scoped Storage `MediaStore` export to Downloads |
| **Telemetry Badges** | RTF badge (green) + VmRSS memory badge (blue) | Real-time RTF badge + Hardware VmRSS badge + C++ kernel timing diagnostics |
| **Session Persistence** | `SharedPreferences` caching transcripts and paths | Android `SharedPreferences` restoring previous sessions across launches |

---

## 3. High-Level Phase Breakdown

```mermaid
flowchart TD
    subgraph Phase 1: Layout & Design System
        P1_1[Material 3 Deep Purple Theme & Tokens] --> P1_2[4-Step Card Visual Hierarchy in activity_main.xml]
    end

    subgraph Phase 2: Audio Recording & Import
        P2_1[Native 24kHz AudioRecord Engine] --> P2_2[Audio File Picker & In-Memory WAV Loader]
        P2_2 --> P2_3[Inline Reference Audio Player Preview]
    end

    subgraph Phase 3: Interactive Presets & BottomSheets
        P3_1[Example Transcripts Modal BottomSheet] --> P3_2[Target Speech Ideas Modal BottomSheet]
        P3_2 --> P3_3[Multilingual Indic Sentence Library]
    end

    subgraph Phase 4: Seekable Audio Player & Telemetry
        P4_1[SeekableAudioPlayer Component with Scrubbing] --> P4_2[LATEST Card with Gradient Aesthetic]
        P4_2 --> P4_3[RTF & VmRSS Pill Badges]
    end

    subgraph Phase 5: Library, History & Export
        P5_1[Generation History Manager & Local Cache] --> P5_2[History RecyclerView with Individual Actions]
        P5_2 --> P5_3[Public Downloads Export via MediaStore]
    end

    subgraph Phase 6: Session Persistence & Polish
        P6_1[SharedPreferences Auto-Save/Restore] --> P6_2[Input Validation & Error Feedback]
        P6_2 --> P6_3[End-to-End On-Device Verification]
    end

    Phase 1 --> Phase 2
    Phase 2 --> Phase 3
    Phase 3 --> Phase 4
    Phase 4 --> Phase 5
    Phase 5 --> Phase 6
```

---

## 4. Phase Specifications

### Phase 1: Theme & 4-Step Card Layout
- **Objective**: Establish the dark Material 3 visual design system and structure the main UI into four clear, numbered steps.
- **Deliverables**:
  - `colors.xml`: Purple accent palette (`#7C4DFF`, `#651FFF`), dark surfaces (`#121212`, `#1E1B2E`), status colors (`#00E676`, `#2979FF`).
  - `activity_main.xml`: 4 discrete section cards with numbered badges (`1`, `2`, `3`, `4`), clear section headers, subtitles, and dividers.

### Phase 2: In-App Voice Recording & Audio File Picker
- **Objective**: Allow users to either record their voice live or pick an external audio file as the reference speaker.
- **Deliverables**:
  - `AudioRecorderHelper.kt`: Microphone recording using `AudioRecord` at 24000 Hz, 16-bit mono PCM. Saves directly to WAV.
  - Runtime permission handling for `RECORD_AUDIO`.
  - `ActivityResultContracts.GetContent` for importing existing WAV files.
  - Active audio status container with file info and audio preview player.

### Phase 3: Interactive Presets & Bottom Sheets
- **Objective**: Provide curated reference transcripts and target text ideas for instant testing.
- **Deliverables**:
  - `ExampleScriptsBottomSheet.kt`: Bottom sheet dialog with 4 preset reference scripts (Conversational, Pangram, Vowel coverage, Narration).
  - `QuickIdeasBottomSheet.kt`: Categorized target text ideas across Short, Medium, and Long lengths, with English, Hindi, Tamil, and Telugu prompts.

### Phase 4: Seekable Audio Player & Telemetry Badges
- **Objective**: Replace blind audio playback with an interactive, seekable media player and prominent telemetry badges.
- **Deliverables**:
  - `SeekableAudioPlayer.kt`: Encapsulated player managing `MediaPlayer` with Play/Pause state, seekable `SeekBar`, and duration timers.
  - Visual telemetry badges: Real-Time Factor (RTF) badge and resident memory (VmRSS) badge.

### Phase 5: Generation Library, History & Downloads Export
- **Objective**: Persist generated audio clips and allow users to manage history and export audio to their phone storage.
- **Deliverables**:
  - `GenerationHistoryManager.kt`: Manages clips in `filesDir/generated/` with metadata (RTF, memory, timestamp).
  - `HistoryAdapter.kt` + `item_history_clip.xml`: RecyclerView showing past clips, individual players, delete, and download buttons.
  - MediaStore export utility to save selected clips into `/storage/emulated/0/Download/`.

### Phase 6: Session Persistence & Polish
- **Objective**: Ensure seamless UX across app restarts and edge-case handling.
- **Deliverables**:
  - `SharedPreferences` integration to restore reference text, audio path, target text, and step count on app restart.
  - Input validation to disable generation until prerequisites are satisfied, with informative warning hints.
  - Final on-device regression test on Galaxy S23.
