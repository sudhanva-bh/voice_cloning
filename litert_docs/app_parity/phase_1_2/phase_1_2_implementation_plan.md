# Phase 1 & 2 Implementation Plan: Layout, Theme, Recording & Audio Import

**Target Module**: `android/app`  
**Goal**: Transform IndicVoice native Android application into the 4-step wizard interface with Material 3 dark styling, live 24 kHz microphone recording, external audio file picking, and reference audio previewing.

---

## 1. Phase 1: Theme & 4-Step Card Layout

### 1.1 Aesthetic & Color Tokens
Align with Flutter prototype's dark mode visual identity:
- **Primary / Brand Accent**: `#7C4DFF` (Deep Purple Accent) / `#651FFF`
- **Background**: `#121212` (True Dark)
- **Card Surface**: `#1E1B2E` (Deep Midnight Purple)
- **Elevated Container**: `#2A2640`
- **Text Primary**: `#FFFFFF`
- **Text Secondary**: `#B0A8D0`
- **Status Green (Accent)**: `#00E676` (Spring Green for Ready states & RTF)
- **Status Blue (Memory)**: `#2979FF` (Electric Blue for VmRSS)
- **Recording Red**: `#FF5252` (Pulsing Red for Recording)

Files to create/modify:
- `android/app/src/main/res/values/colors.xml`: Add purple and telemetry palette tokens.
- `android/app/src/main/res/values/themes.xml`: Set Material 3 dark theme with custom card styling.
- `android/app/src/main/res/drawable/card_step_header_badge.xml`: Circular purple badge for step numbers (`1`, `2`, `3`, `4`).
- `android/app/src/main/res/drawable/bg_latest_card_gradient.xml`: Linear gradient for the "LATEST" output card.

### 1.2 Layout Structure (`activity_main.xml`)
Re-architect the layout into a vertically scrolling `ScrollView` containing:
1. **Header Banner**: "IndicVoice Studio" + "On-Device Neural Voice Cloning • LiteRT INT8".
2. **Step 1 Card**:
   - Number badge `1` + "Reference Script (Transcript)".
   - Action buttons: "Example Scripts" (outlined button) and "Clear" (text button).
   - Multi-line `EditText` for the reference speaker transcript.
3. **Step 2 Card**:
   - Number badge `2` + "Reference Voice Audio".
   - Split action buttons: "Record Audio" (`#7C4DFF` / `#FF5252` when active) + "Upload File" (outlined button).
   - Ready state container: Shown when audio is loaded. Features green check icon, clip filename, duration, preview play button, "Upload new", "Reset", and "Re-record" actions.
4. **Step 3 Card**:
   - Number badge `3` + "Target Speech Text".
   - Quick action buttons: "Quick Ideas" modal trigger + "Clear".
   - Language quick-pills: English, Hindi, Telugu, Tamil.
   - CFM Step selection: 8 (Fast), 16 (Balanced), 24 (HQ).
   - Multi-line `EditText` for the synthesis target.
   - Prominent "Generate Cloned Speech" button with loading spinner.
   - Dynamic validation warning text below button (e.g., "⚠️ Step 2 audio required before generating").
5. **Step 4 Card**:
   - Number badge `4` + "Generated Speech & Library".
   - "LATEST" gradient card with RTF badge, VmRSS badge, and inline audio playback.
   - Placeholder state when no generation has occurred yet.

---

## 2. Phase 2: In-App Voice Recording & Audio File Picker

### 2.1 Native 24 kHz Audio Recording (`AudioRecorderHelper.kt`)
IndicF5 DiT + Vocos operates natively at **24,000 Hz**.
- Use native `android.media.AudioRecord` directly:
  ```kotlin
  val sampleRate = 24000
  val channelConfig = AudioFormat.CHANNEL_IN_MONO
  val audioFormat = AudioFormat.ENCODING_PCM_16BIT
  ```
- Record in a background thread/coroutine writing directly to a temporary file.
- On stop, write a standard 44-byte RIFF WAV header wrapping the raw PCM bytes:
  - Format: PCM (1)
  - Channels: 1 (Mono)
  - Sample Rate: 24000
  - Byte Rate: 48000
  - Bits Per Sample: 16
- Return the absolute path of the finalized WAV file.

### 2.2 Permissions Management
- Declare `android.permission.RECORD_AUDIO` in `AndroidManifest.xml`.
- Implement runtime permission check using `ActivityResultContracts.RequestPermission()`.
- Display informative dialog if permission is denied.

### 2.3 Audio File Picker
- Implement `ActivityResultContracts.GetContent()` for `audio/*`.
- When an audio URI is returned:
  - Copy stream into internal cache: `File(cacheDir, "picked_reference.wav")`.
  - Validate WAV header (must start with ASCII `"RIFF"` and `"WAVE"`).
  - Inspect sample rate from byte offset 24..27. If it's already 24kHz mono PCM, load immediately.
  - If 16kHz or 48kHz, automatically resample or pass through `AudioProcessor`.

### 2.4 Reference Audio Preview Player
- Add preview playback capability directly inside the Step 2 "Ready State" container.
- Simple Play / Pause button that plays the currently loaded reference WAV clip so the user can verify their recording before running synthesis.

---

## 3. Verification & Acceptance Criteria
1. **Visual Parity**: Layout displays all 4 numbered step cards matching the dark purple Material 3 theme.
2. **Mic Recording**: Pressing "Record Audio" requests permission (if needed), records mic audio at 24kHz mono, updates UI to red "Stop Recording", and writes a valid WAV file upon stop.
3. **Audio File Picker**: Pressing "Upload File" opens the Android system file picker, loads selected audio, and updates Step 2 with the file name.
4. **Audio Preview**: The recorded or picked WAV can be played back instantly inside Step 2.
5. **End-to-End Synthesis**: Triggering synthesis with the newly recorded/picked reference audio completes inference with 0 NaNs and produces clear cloned audio.
