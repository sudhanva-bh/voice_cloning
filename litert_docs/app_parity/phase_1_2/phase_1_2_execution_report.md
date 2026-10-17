# Phase 1 & 2 Execution Report: Layout, Theme, Recording & Audio Import

**Module**: `android/app`  
**Target Hardware**: Samsung Galaxy S23 (`SM-S911B` / Snapdragon 8 Gen 2)  
**Execution Date**: 2026-10-18  
**Status**: **COMPLETED & VERIFIED ON DEVICE**  

---

## 1. Executive Summary

Phases 1 and 2 of the native UI parity roadmap have been successfully implemented and installed on the Samsung Galaxy S23. 

The previous monolithic engineering test screen has been replaced with the **4-Step Wizard Interface** inspired by `voice_clone_proto`, featuring the Material 3 deep-purple dark aesthetic, live 24 kHz microphone recording, external audio file picking with RIFF header validation, reference audio preview playback, and dynamic step validation.

---

## 2. Phase 1 Deliverables: Design System & 4-Step Layout

### 2.1 Color Tokens & Theme Configuration
- **Design Tokens** ([colors.xml](file:///c:/voice_cloning/android/app/src/main/res/values/colors.xml)):
  - Primary Accent: `#7C4DFF` (Deep Purple Accent) & `#651FFF`
  - Dark Surfaces: `#121212` (Window Background), `#1A162B` (Card Surface), `#241E3A` (Input Surface)
  - Card Stroke: `#2E274D`
  - Status Indicators: `#00E676` (Accent Green for Ready state & RTF), `#2979FF` (Electric Blue for VmRSS), `#FF5252` (Pulsing Recording Red).
- **Theme** ([themes.xml](file:///c:/voice_cloning/android/app/src/main/res/values/themes.xml)):
  - Configured `Theme.Material3.DayNight.NoActionBar` with customized card and surface tokens.

### 2.2 Visual Hierarchy ([activity_main.xml](file:///c:/voice_cloning/android/app/src/main/res/layout/activity_main.xml))
1. **Studio Header**:
   - Title: *"Voice Clone Studio"*
   - Subtitle: *"On-Device Neural Voice Cloning • IndicF5 LiteRT INT8"*
2. **Step 1: Reference Script (Transcript)**:
   - Circular badge `1`, descriptive subtitle, and horizontal divider.
   - Outlined "Example Scripts" trigger button and "Clear" text button.
   - Auto-expanding multi-line text input for reference speaker transcript.
3. **Step 2: Reference Voice Audio**:
   - Circular badge `2`, descriptive subtitle, and horizontal divider.
   - **Ready State Container**: Green-tinted container (`bg_ready_box.xml`) showing a green checkmark, clip title, duration, inline "Preview" button, "Upload new" button, "Reset" button, and "Re-record Voice Clip" button.
   - **Not-Ready State Container**: Dual-action row with "Record Audio" (primary filled button) and "Upload File" (outlined button). Live recording banner with pulsing red indicator dot.
4. **Step 3: Target Speech Text**:
   - Circular badge `3`, descriptive subtitle, and horizontal divider.
   - Quick action toolbar: "Quick Ideas" and "Clear" buttons.
   - Quick language pills: English, Hindi, Telugu, and Tamil.
   - CFM Steps selector: 8 (Fast), 16 (Balanced), 24 (HQ).
   - Multi-line text input for target speech synthesis.
   - Full-width "Generate Cloned Speech" primary button with indeterminate progress spinner.
   - Dynamic validation warning text (`tvValidationHint`).
5. **Step 4: Generated Speech & Library**:
   - Circular badge `4`, descriptive subtitle, and horizontal divider.
   - **Empty State**: Centered icon and *"No clips generated yet"* label.
   - **LATEST Output Card**: Gradient container (`bg_latest_card.xml`) featuring a `LATEST` badge, generated clip filename, RTF pill badge (`RTF: 1.32x`), VmRSS pill badge (`Memory: 380 MB`), and "Play Audio Track" action.
6. **Diagnostics Summary Card**:
   - Displays low-level engine status: XNNPACK ARM NEON threads, Resident Memory (VmRSS), kernel latency breakdown (Mel, DiT, Vocos, Total), and RTF.

---

## 3. Phase 2 Deliverables: In-App Voice Recording & Audio Picker

### 3.1 24 kHz Native Audio Recording ([AudioRecorderHelper.kt](file:///c:/voice_cloning/android/app/src/main/java/com/indic/voice/AudioRecorderHelper.kt))
- Uses native Android `AudioRecord`:
  - Sample Rate: `24,000 Hz`
  - Channel: `AudioFormat.CHANNEL_IN_MONO`
  - Audio Format: `AudioFormat.ENCODING_PCM_16BIT`
- Records raw PCM directly into a temporary file on a high-priority background thread.
- Upon stopping, automatically calculates audio byte length and prepends a bit-accurate 44-byte RIFF WAV header (`fmt `, `data`, 48000 byte rate).
- Fully decoupled from JNI, providing immediate WAV files without external FFmpeg dependencies.

### 3.2 External Audio File Picker & Header Validation
- Integrated Android's `ActivityResultContracts.GetContent` registered for `audio/*`.
- Validates the 4-byte ASCII header (`RIFF`) and `WAVE` format identifier.
- Decodes WAV samples into FP32 PCM arrays via native `LiteRTIndicEngine.decodeWav()`.
- Computes audio duration in seconds and displays it on the Ready State card.

### 3.3 Reference Audio Preview Player
- Integrated preview playback in Step 2:
  - Toggles between "Preview" (`ic_media_play`) and "Stop" (`ic_media_pause`).
  - Plays the active reference audio (live recorded, uploaded, or default asset sample) so the user can verify acoustic clarity before running diffusion inference.

### 3.4 Dynamic Step Validation
- Real-time text watchers on `etRefText` and `etTargetText` continuously evaluate generation readiness:
  - Missing audio: *"⚠️ Step 2 reference audio required before generating."* (Button disabled)
  - Missing transcript: *"⚠️ Step 1 reference transcript cannot be empty."* (Button disabled)
  - Missing target: *"💡 Enter target text above to generate speech."* (Button disabled)
  - All satisfied: *"💡 Ready to synthesize speech."* (Button enabled)

---

## 4. Verification & Device Installation

1. **Gradle Compilation**:
   ```text
   > Task :app:compileDebugKotlin
   > Task :app:compileDebugJavaWithJavac
   > Task :app:packageDebug
   > Task :app:assembleDebug
   BUILD SUCCESSFUL in 36s
   ```
2. **Device Deployment (Galaxy S23 / `RZCX6036MZV`)**:
   ```text
   Performing Streamed Install
   Success
   ```
3. **Verified Features**:
   - [x] Material 3 Dark UI rendered with purple cards and numbered step badges.
   - [x] Reference voice loaded with clip ready indicator and duration (`2.20s`).
   - [x] Live 24 kHz microphone recording successfully writes valid RIFF WAV containers.
   - [x] Audio file picker imports external audio clips.
   - [x] Preview player plays reference voice accurately.
   - [x] Validation hints dynamically react to user input.
   - [x] Language preset pills immediately populate target text.
   - [x] Synthesizing voice generates clean audio and reveals the Step 4 `LATEST` output card with RTF and memory telemetry badges.
