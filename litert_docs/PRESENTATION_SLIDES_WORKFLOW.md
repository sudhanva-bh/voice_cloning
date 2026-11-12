# On-Device Multilingual Voice Cloning: End-to-End Workflow & Architecture Slide Deck

**Document Title**: Presentation Slide Deck — End-to-End App Workflow, Underlying Neural Architecture, and Edge Optimization  
**File**: `c:\voice_cloning\PRESENTATION_SLIDES_WORKFLOW.md`  
**Target Audience**: Academic Evaluators, Thesis Defense Committee, ML / Edge Systems Engineers  
**Target Platform**: Android Mobile Devices (Snapdragon 8 Gen 2 / MediaTek Helio P22T)  
**Core Technologies**: Google LiteRT, IndicF5 (Diffusion Transformer), Vocos Vocoder, C++20 NDK, Kotlin Coroutines, XNNPACK ARM NEON  

---

## Slide Index & Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Master Presentation Outline                                     │
├───────┬────────────────────────────────────────────────────────┬───────────────────────────────────────┤
│ Slide │ Slide Title                                            │ Category                              │
├───────┼────────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 01    │ Title Slide: On-Device Multilingual Voice Cloning      │ Introduction                          │
│ 02    │ The Problem Landscape: The Tri-Factor Challenge        │ Motivation & Context                  │
│ 03    │ Dual-Perspective Architecture Overview                 │ System Architecture                   │
│ 04    │ Architectural Pivot: Native C++ NDK vs. Flutter        │ Edge Systems Engineering              │
│ 05    │ Step 1 (App): Reference Audio Capture & Validation     │ App Workflow: Input Stage             │
│ 06    │ Step 1 (Underlying): Mel Filterbank DSP & Extraction   │ Deep-Dive: Audio Preprocessing        │
│ 07    │ Step 2 (Underlying): Speaker Conditioning Mel Caching  │ Deep-Dive: Native Engine Optimization │
│ 08    │ Step 3 (App): Multilingual Target Text & Presets       │ App Workflow: Text Input Stage        │
│ 09    │ Step 3 (Underlying): Hierarchical Multilingual Chunker │ Deep-Dive: NLP & Window Budgeting     │
│ 10    │ Step 4 (Hardware): Step Scaling & CPU Core Tuning      │ Deep-Dive: Snapdragon 8 Gen 2 Tuning  │
│ 11    │ Step 5 (Underlying): CFM Diffusion & DiT INT8 Engine   │ Deep-Dive: Neural Inference           │
│ 12    │ Step 5 (Math): Low-Step Distortion & 3-Tier Stability  │ Deep-Dive: Mathematical Optimization  │
│ 13    │ Step 6 (Underlying): Vocos Vocoder & iSTFT Synthesis   │ Deep-Dive: Acoustic Decoding          │
│ 14    │ Step 7 (Underlying): Waveform Stitcher & Hann Fades    │ Deep-Dive: Audio Post-Processing      │
│ 15    │ Step 8 (App): Seekable Playback, Telemetry & Export    │ App Workflow: Output & Persistence    │
│ 16    │ Step 8 (Underlying): Sharing Truncation & 450ms Buffer │ Deep-Dive: OS Transcoder Resilience   │
│ 17    │ Quantitative Empirical Benchmarks: Galaxy S23          │ Experimental Results                  │
│ 18    │ Spectral Quality & Parity: 2.14 dB MCD Verification    │ Experimental Results                  │
│ 19    │ Technical Contributions & Key Engineering Takeaways    │ Summary & Impact                      │
│ 20    │ Conclusion, Live Demonstration & Future Roadmap        │ Conclusion & Q&A                      │
└───────┴────────────────────────────────────────────────────────┴───────────────────────────────────────┘
```

---

## Slide 01: Title Slide

### Header
**On-Device Multilingual Voice Cloning & Zero-Shot Speech Synthesis**  
*Ultra-Low Latency Flow Matching with Google LiteRT on Mobile Hardware*

### Subtitle & Metadata
- **Presenter**: Sudhanva B H
- **Academic Guidance**: Dr. Jabez Christopher
- **Institution**: BITS Pilani, Hyderabad Campus
- **Repository**: `c:\voice_cloning`
- **Target Languages**: Tamil (Native Primary), Telugu, Kannada, Hindi, English

### Visual Layout & Graphic Elements
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                  │
│       🎙️ 3–5s Reference Audio (Any Speaker)  ───►  [ On-Device LiteRT INT8 ]                     │
│                                                              │                                   │
│       📝 Target Text (Tamil / Telugu / Hindi / Eng) ─────────┘                                   │
│                                                              │                                   │
│                                                              ▼                                   │
│                                                    🔊 Cloned Voice Waveform                      │
│                                           (Zero Cloud • 385 MB RAM • RTF 1.5x)                   │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaker Notes
> "Good morning, respected committee members and fellow researchers. Today, I am presenting our work on **On-Device Multilingual Voice Cloning and Zero-Shot Speech Synthesis using Google LiteRT**.
> 
> Voice cloning typically relies on massive cloud clusters running 10-billion parameter models with multi-second server roundtrips. Our goal was fundamentally different: to achieve zero-shot voice cloning from just 3 to 5 seconds of reference audio, running completely offline and privately on commodity Android mobile phones, supporting Indian languages like Tamil, Telugu, and Hindi alongside English.
> 
> In this presentation, I will walk you through both perspectives: the smooth user-facing workflow of our production native Android application, and the deep, underlying mathematical, neural, and C++ systems engineering that makes it possible."

---

## Slide 02: The Problem Landscape — The Tri-Factor Challenge

### Category
Motivation & Problem Context

### Slide Title
**The Tri-Factor Challenge in Edge Neural Voice Cloning**

### Visual Layout (Three-Circle Venn Diagram / Callout Columns)
```
                                 ┌─────────────────────────┐
                                 │   1. Native Indic       │
                                 │      Phonetics          │
                                 └────────────┬────────────┘
                                             / \
                                            /   \
                                           /  ★  \  ◄── "Target Intersection:
                                          /       \      Zero off-the-shelf
                                         /         \     models exist here"
                                        /           \
              ┌────────────────────────┴────┐   ┌────┴────────────────────────┐
              │ 2. True Zero-Shot Cloning   │───│ 3. Strict Mobile Limits     │
              │    (Timbre & Cadence Copy)  │   │    (<=4GB RAM, Low RTF, CPU)│
              └─────────────────────────────┘   └─────────────────────────────┘
```

### Key Bullet Points
- **Challenge 1: Native Indic Phonetics & Abugida Scripts**:
  - Western TTS models (Kokoro, standard F5-TTS) fail completely on Indian languages.
  - Indian scripts rely on syllabic *aksharas*, vowel ligatures (*matras*), and consonant conjuncts requiring language-specific character vocabulary and duration allocation.
- **Challenge 2: Instant Zero-Shot Timbre Transfer**:
  - Must capture vocal identity, pitch contour, and emotional cadence from 3–5s of audio without speaker fine-tuning.
  - Autoregressive models (e.g., XTTS-v2) are sequential, memory-heavy, and prone to hallucinations on short clips.
- **Challenge 3: Severe Edge Hardware Constraints**:
  - Target deployment includes budget tablets like the **Lenovo Tab K10** (MediaTek Helio P22T, 4 GB RAM, no NPU, ~1.5 GB user-space limit before the Linux `LowMemoryKiller` terminates the app).
  - Must maintain a deterministic memory footprint under 500 MB while delivering conversational real-time factors (RTF).

### Speaker Notes
> "Why is on-device voice cloning for Indian languages so difficult? It sits at the intersection of three competing constraints.
> 
> First, linguistic complexity: Indian languages are non-Latin abugida scripts where characters represent full syllables (*aksharas*) rather than individual letters. Existing open-source edge models are predominantly trained on English or Chinese.
> 
> Second, zero-shot transfer: We cannot spend 10 minutes fine-tuning weights for every new user. The model must ingest raw audio and immediately mimic the timbre in-context.
> 
> Third, hardware limitations: While flagship phones have fast NPUs, mass-market educational devices like the Lenovo Tab K10 have only 4 GB of total system RAM and low-power Cortex-A53 CPU cores. If our app uses more than 1.5 GB, Android's `LowMemoryKiller` kills the process instantly. Our system addresses all three constraints simultaneously."

---

## Slide 03: Dual-Perspective Architecture Overview

### Category
System Architecture

### Slide Title
**Dual-Perspective Architecture: App UX vs. Underlying Pipeline**

### Visual Layout (Split View / Two-Track Flowchart)
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FRONT-END: Native Android User Experience (Kotlin 4-Step Wizard UI)                              │
│                                                                                                  │
│   [ Step 1: Script ] ──► [ Step 2: Audio ] ──► [ Step 3: Text ] ──► [ Step 4: Player & Share ]   │
│   • Multi-line input     • 24kHz Recorder      • Quick Ideas         • Seekable Player           │
│   • Example Scripts      • File Picker         • 12/16/24 Steps      • MediaStore Export         │
│   • Validation State     • Live Preview        • Progress Tracker    • FileProvider Share        │
└────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                         │ JNI Bridge (liblitert_indic.so)
┌────────────────────────────────────────▼─────────────────────────────────────────────────────────┐
│ BACK-END: Underlying Systems & Neural Inference Pipeline (C++20 NDK + Google LiteRT)             │
│                                                                                                  │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐            │
│   │ Audio DSP     │────►│ Speaker Mel   │────►│ Multilingual  │────►│ CFM DiT INT8  │──┐         │
│   │ 24kHz Mel FFT │     │ Native Cache  │     │ Chunker       │     │ Euler ODE     │  │         │
│   └───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘  │         │
│                                                                                        ▼         │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐  │         │
│   │ 450ms Comfort │◄────│ Asymmetric    │◄────│ Waveform      │◄────│ Vocos Neural │◄─┘         │
│   │ Silence Buffer│     │ Trimming      │     │ Stitcher      │     │ iSTFT Vocoder │            │
│   └───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘            │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Bullet Points
- **User-Facing Layer (Kotlin)**:
  - Material 3 Dark Wizard UI guiding users through Transcript $\to$ Audio $\to$ Target Text $\to$ Generation.
  - Real-time hardware telemetry display: Resident Memory (`VmRSS`), Real-Time Factor (`RTF`), and kernel latency.
- **Underlying Engine Layer (C++20 & LiteRT)**:
  - Zero-allocation memory management, native Mel-spectrogram extraction, and speaker condition caching.
  - Continuous Flow Matching (CFM) ODE solver with vectorized ARM NEON execution across 5 CPU cores.

### Speaker Notes
> "This slide illustrates the core dual-track architecture of our solution.
> 
> On the top track, you see the user experience: a clean, 4-step wizard interface built in Kotlin following Google's Material 3 design guidelines. It manages microphone permissions, file picking, preset selection, dynamic progress streaming, and one-tap audio sharing.
> 
> On the bottom track, you see what happens beneath the surface in C++: raw audio is converted to a log-mel spectrogram, the speaker conditioning is cached in native memory, the text is chunked into phonetically balanced segments, and an 8-bit quantized Diffusion Transformer solves an Ordinary Differential Equation across 5 CPU cores. The audio is then vocoded via Vocos, stitched with Hann crossfades, padded with comfort silence, and played back."

---

## Slide 04: The Architectural Pivot — Native C++ NDK vs. Flutter

### Category
Edge Systems Engineering

### Slide Title
**Why We Abandoned Flutter for Direct Native Android (C++ NDK)**

### Visual Comparison Table
```
┌──────────────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
│ Engineering Dimension                │ Flutter Prototype (Initial) │ Direct Native C++ NDK (Now) │
├──────────────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Baseline Idle RAM (Dart VM + Skia)   │ ~150 MB                     │ **~45 MB** (70% Reduction)  │
│ Peak Synthesis RAM (VmRSS)           │ ~1,280 MB – 1,560 MB        │ **~385 MB** (Deterministic) │
│ FFI Data Marshalling Overhead        │ High (Marshalled 32x/chunk) │ **Zero** (Direct C++ ptrs)  │
│ Thread Contention                    │ Dart isolate vs. XNNPACK    │ Direct CPU thread binding   │
│ APK Installation Size                │ ~95 MB (Flutter engines)    │ **~32 MB** (Lean NDK app)   │
│ Audio I/O Overhead                   │ FFmpegKit process wrapper   │ Native AudioRecord / PCM    │
│ Safety Margin on 4GB Devices         │ Dangerously close to OOM    │ **>1,000 MB Safety Cushion**│
└──────────────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

### Key Bullet Points
- **The Memory Wall**: In our early Flutter prototype, the Dart Virtual Machine, platform channels, and Flutter engine consumed 150 MB before inference even started.
- **Zero-Copy Performance**: In native C++, large multi-dimensional audio buffers ($512 \times 100$ floats) never cross a language barrier; they are mapped directly to LiteRT tensor memory via `TfLiteTensorData()`.
- **Thread Determinism**: Eliminated thread synchronization stutter between Dart's event loop and XNNPACK's ARM NEON thread pool.

### Speaker Notes
> "One of our most critical engineering decisions was pivoting away from Flutter.
> 
> Our early prototypes were built in Flutter because of its rapid UI development. However, profiling on physical hardware revealed that the Dart VM and Skia engine consumed 150 MB of baseline RAM. During 16-step flow matching, crossing the Dart-to-C++ FFI boundary 32 times per chunk introduced measurable thread contention and GC pauses.
> 
> By rebuilding directly in native Android using Kotlin and C++20 NDK, we slashed idle memory from 150 MB down to 45 MB, reduced peak resident memory to an ultra-stable 385 MB, and completely eliminated data copying. This single decision made deployment on 4 GB budget tablets 100% stable."

---

## Slide 05: Step 1 (App View) — Reference Audio Capture & Validation

### Category
App Workflow: Input Stage

### Slide Title
**Step 1: Reference Audio Selection, Live Recording & Validation**

### Visual Layout (UI Card Mockup & Flow)
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: REFERENCE VOICE AUDIO                                                                  │
│  Provide 3–5 seconds of clean speech from the speaker you want to clone.                         │
│                                                                                                  │
│  [ STATE A: NOT READY ]                     [ STATE B: READY (AFTER CAPTURE) ]                   │
│  ┌────────────────────────────────────┐     ┌──────────────────────────────────────────────────┐ │
│  │  [🎙️ Record Audio]  [📁 Upload File]│     │  ✅ Clip Ready (ref_tamil.wav • 3.82s)           │ │
│  │                                    │     │  [▶ Play Preview] [🔄 Re-record] [Upload New]    │ │
│  │  🔴 Recording live... (Pulsing Dot)│     │  00:00 ───●────────────────────────────── 00:03 │ │
│  └────────────────────────────────────┘     └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Bullet Points
- **Dual Capture Methods**:
  - *Option A: Live In-App Recording*: Native 24 kHz mono recording with dynamic microphone permission handling.
  - *Option B: Audio File Picker*: Integration with Android `ActivityResultContracts.GetContent` for external WAV/MP3 files.
- **Real-Time RIFF Header Validation**:
  - Automatically parses the 44-byte RIFF/WAVE header to verify sampling rate, channels, and bit depth.
- **Interactive Seekable Preview**:
  - Embedded `SeekableAudioPlayerView` lets the user listen to and scrub through their recording to verify acoustic clarity before running synthesis.
- **Dynamic State Machine**:
  - Green checkmark container surfaces file name and duration, immediately unlocking the generation pipeline.

### Speaker Notes
> "Let us look at Step 1 from the user's perspective.
> 
> The user needs to provide a 3 to 5 second voice sample. They can either tap 'Record Audio' to capture their voice live, or tap 'Upload File' to pick a pre-recorded clip.
> 
> We implemented custom RIFF header validation: if a user uploads a malformed file or an incompatible sampling rate, the app catches it immediately. Once valid audio is captured, the UI transitions to the green 'Ready' card, displaying the clip title, exact duration, and an embedded player so the user can verify their audio before continuing."

---

## Slide 06: Step 1 (Underlying View) — Mel Filterbank DSP & Extraction

### Category
Deep-Dive: Audio Preprocessing

### Slide Title
**Underlying Audio DSP: 100-Channel Log-Mel Spectrogram Extraction**

### Mathematical Formulations & DSP Specs
$$\text{Mel}(f) = 2595 \log_{10}\left(1 + \frac{f}{700}\right)$$
$$\text{LogMel}(m, t) = \log\left(\sum_{k=0}^{K-1} |X(k, t)|^2 \cdot H_m(k) + \epsilon\right)$$

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Audio DSP Parameter Configuration Matrix                                                         │
├──────────────────────────┬──────────────────────────┬────────────────────────────────────────────┤
│ Sampling Rate ($f_s$)    │ 24,000 Hz (Mono PCM)     │ Broadcast standard speech fidelity         │
│ FFT Window Length ($N$)  │ 1,024 samples (42.6 ms)  │ Provides high frequency resolution         │
│ Hop Length ($R$)         │ 256 samples (10.6 ms)    │ 93.75 frames per second temporal grid      │
│ Mel Filterbank Bins ($M$)│ 100 Triangular Bins      │ Captures fine formant & pitch structures   │
│ Frequency Bounds         │ 0 Hz to 12,000 Hz        │ Full Nyquist bandwidth                     │
│ Normalization            │ RMS Normalization + eps  │ Calibrates dynamic range across speakers   │
└──────────────────────────┴──────────────────────────┴────────────────────────────────────────────┘
```

### Key Implementation Details
- Hand-crafted, zero-dependency C++ mel filterbank in [`mel_filterbank.h`](file:///c:/voice_cloning/android/app/src/main/cpp/mel_filterbank.h).
- Precomputed triangular filter weights eliminating trigonometric runtime overhead.
- Bit-accurate parity with PyTorch's `torchaudio.transforms.MelSpectrogram`.

### Speaker Notes
> "Now, what happens under the hood when that audio is captured?
> 
> In [`audio_processor.cpp`](file:///c:/voice_cloning/android/app/src/main/cpp/audio_processor.cpp), the float PCM audio is converted into a 100-channel log-mel spectrogram.
> 
> We sample at 24,000 Hz with a 1024-point FFT window and a hop length of 256 samples. This generates roughly 94 mel frames per second. We built a native C++ triangular filterbank that maps linear frequencies up to 12 kHz onto the nonlinear perceptual Mel scale.
> 
> The extraction includes RMS volume normalization, ensuring that whether a user whispers or speaks loudly into the phone, the conditioning spectrogram enters the neural network with a normalized dynamic range."

---

## Slide 07: Step 2 (Underlying View) — Speaker Conditioning Mel Caching

### Category
Deep-Dive: Native Engine Optimization

### Slide Title
**Speaker Conditioning Cache: Eliminating 90% of Redundant Computation**

### Visual Architecture Flowchart
```
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │ TRADITIONAL UNCACHED MULTI-CHUNK PIPELINE (WASTEFUL)                                        │
  │ Chunk 1: [Extract Ref Mel (180ms)] ──► [DiT ODE] ──► [Vocos]                                │
  │ Chunk 2: [Extract Ref Mel (180ms)] ──► [DiT ODE] ──► [Vocos]  ◄── 180ms wasted EVERY chunk! │
  │ Chunk 3: [Extract Ref Mel (180ms)] ──► [DiT ODE] ──► [Vocos]                                │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │ OUR CACHED NATIVE ARCHITECTURE (OPTIMAL)                                                    │
  │ setReferenceAudio(): [Extract Ref Mel ONCE (180ms)] ──► Store in cached_ref_mel_ (C++ RAM)   │
  │                                                                                             │
  │ Chunk 1: synthesizeChunk() ──► [Re-use Cached Mel (0ms)] ──► [DiT ODE] ──► [Vocos]         │
  │ Chunk 2: synthesizeChunk() ──► [Re-use Cached Mel (0ms)] ──► [DiT ODE] ──► [Vocos]         │
  │ Chunk 3: synthesizeChunk() ──► [Re-use Cached Mel (0ms)] ──► [DiT ODE] ──► [Vocos]         │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Engineering Features
- **Separation of Concerns in C++ API**:
  - `setReferenceAudio(ref_pcm, ref_text)`: Runs once when reference audio changes. Extracts mel frames, tokenizes reference text, and validates timbre characteristics.
  - `synthesizeChunk(chunk_text)`: Executes purely the diffusion ODE and vocoder for the new sentence.
- **Acoustic Consistency**:
  - Guaranteeing that chunk 1, chunk 2, and chunk 5 are conditioned on the exact same spectral representation, preventing "speaker timbre drift" across long paragraphs.

### Speaker Notes
> "In long-form speech synthesis, an utterance is split into multiple sentences.
> 
> A naive implementation re-extracts the reference audio Mel-spectrogram for every single sentence. If you synthesize a 5-sentence paragraph, you perform the FFT and filterbank calculations 5 separate times, wasting CPU cycles and battery.
> 
> In Phase B, we split our native C++ engine into `setReferenceAudio()` and `synthesizeChunk()`. The speaker's mel features are extracted once and held in a pre-allocated C++ float buffer. Every subsequent chunk reuses this cached memory with zero extraction latency. Furthermore, this guarantees that the speaker's vocal identity remains perfectly identical across all sentences without timbre drift."

---

## Slide 08: Step 3 (App View) — Multilingual Target Text & Presets

### Category
App Workflow: Text Input Stage

### Slide Title
**Step 3: Target Text Input, Multilingual Presets & Personas**

### Visual Layout (BottomSheet & Input Card Wireframe)
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: TARGET SPEECH TEXT & SYNTHESIS CONTROLS                                                │
│  Enter the text you want the cloned voice to speak.                                              │
│                                                                                                  │
│  [📝 Multi-line Text Input: "Good morning, everyone! Let's quickly revise yesterday's lesson."]  │
│                                                                                                  │
│  [💡 Quick Ideas Button]  [🗑️ Clear]                                                            │
│                                                                                                  │
│  MODAL BOTTOM SHEET: QUICK IDEAS LIBRARY                                                         │
│  ┌────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Filter Chips: [ All ] [ English ] [ हिंदी ] [ తెలుగు ] [ தமிழ் ]                             │  │
│  ├────────────────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 🎓 TEACHER PERSONA: "Good morning! Let's quickly revise what we learned yesterday."        │  │
│  │    Badge: Short (~2.5s) • English • 11 words                                               │  │
│  ├────────────────────────────────────────────────────────────────────────────────────────────┤  │
│  │ ☕ CASUAL FRIEND PERSONA: "अरे सुनो, आज शाम को चाय पीने चलोगे?"                              │  │
│  │    Badge: Short (~2.5s) • Hindi • 7 words                                                  │  │
│  ├────────────────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 📚 EDUCATIONAL PARAGRAPH: "పిల్లలూ, ఈ రోజు మనం వర్షం ఎలా పడుతుందో తెలుసుకుందాం..."          │  │
│  │    Badge: Paragraph (~15s) • Telugu • 42 words                                             │  │
│  └────────────────────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Bullet Points
- **Multilingual Support**: First-class support for English, Hindi (हिंदी), Telugu (తెలుగు), and Tamil (தமிழ்).
- **Curated Personas**:
  - *Teacher Persona*: Structured, educational prompts designed for classroom instruction and storytelling.
  - *Casual Friend Persona*: Colloquial, everyday conversational dialogue.
- **Duration Tiers**: Each preset displays estimated audio length: Short (~2.5s), Medium (~7s), and full Paragraph (~15s).

### Speaker Notes
> "Now let us move to Step 3: defining what the cloned voice should say.
> 
> The user can type any arbitrary text in English, Hindi, Telugu, or Tamil. To make testing seamless, we built the 'Quick Ideas' modal bottom sheet.
> 
> We curated two distinct personas based on user feedback: a 'Teacher Persona' for formal educational instruction, and a 'Casual Friend Persona' for everyday conversational speech.
> 
> Presets are organized into three duration tiers: Short 2.5-second sentences, Medium 7-second phrases, and full 15-second paragraphs. Tapping any card populates the text field and triggers the validation state machine."

---

## Slide 09: Step 3 (Underlying View) — Hierarchical Multilingual Chunker

### Category
Deep-Dive: NLP & Window Budgeting

### Slide Title
**The 512-Frame Barrier & Hierarchical Multilingual Chunker**

### The Problem: The 512-Frame Window Budget
```
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │                      512-Frame Static Model Budget (5.46s Total Audio)                      │
  ├─────────────────────────────────────────────┬───────────────────────────────────────────────┤
  │ Reference Audio Conditioning                │ Remaining Target Speech Budget                │
  │ ~3.8s (356 mel frames)                      │ ONLY ~1.66s (156 mel frames)                  │
  └─────────────────────────────────────────────┴───────────────────────────────────────────────┘
  * Unchunked 60-word paragraph forced into 156 frames -> "Auctioneer Effect" (Speedup + Distortion)
```

### The Solution: Two-Tier Hierarchical Segmentation (`MultilingualChunker.kt`)
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Arbitrary Long Paragraph (e.g., 75 words)                                                        │
└───────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: Terminal Sentence Punctuation Split ([. ! ? । ॥ \n])                                     │
│ • Protects abbreviations: "Dr.", "Mr.", "i.e.", "e.g.", "vs."                                   │
└───────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TIER 2: Clause & Boundary Split (If chunk > 44 Indic / 60 English characters)                    │
│ • Splits on commas, semicolons, colons, dashes ([, ; : \u2014 -])                                 │
│ • Merges residual fragments (< 12 chars) with adjacent chunks                                    │
└───────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Result: Safe, Phonetically Complete Chunks (Each cleanly fitting <= 280 mel frames)              │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaker Notes
> "Why was chunking necessary? This is one of the most interesting systems challenges in our project.
> 
> Our INT8 DiT FlatBuffer was compiled with a fixed sequence budget of 512 frames—about 5.46 seconds of total audio. If the reference audio is 3.8 seconds, you only have 1.66 seconds left for target speech!
> 
> Previously, if you fed a 60-word paragraph into the engine, the Euler ODE solver squeezed all 60 words into that tiny 1.66-second window. The result was the 'auctioneer effect'—audio that was comically fast-forwarded and phonetically garbled.
> 
> In Phase A, we built `MultilingualChunker.kt`. It performs hierarchical two-tier segmentation: first splitting on terminal punctuation while protecting abbreviations like 'Dr.' or 'Mr.', and then splitting oversized sentences on clause boundaries. It limits chunks to 44 characters for Indic scripts and 60 for English, guaranteeing that every single chunk fits safely inside the 512-frame model window."

---

## Slide 10: Step 4 (Hardware View) — Step Scaling & CPU Core Tuning

### Category
Deep-Dive: Snapdragon 8 Gen 2 Tuning

### Slide Title
**Snapdragon 8 Gen 2 CPU Core Tuning & Step Scaling**

### Visual Hardware Core Allocation Diagram
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Snapdragon 8 Gen 2 (SM8550) Asymmetric 8-Core Cluster Architecture                               │
│                                                                                                  │
│   [Core 0: Cortex-X3 Prime @ 3.36 GHz]  ──►  ★ Thread 1 (XNNPACK Heavy GEMM)                     │
│   [Core 1: Cortex-A715 Perf @ 2.80 GHz] ──►  ★ Thread 2 (XNNPACK Attention)                     │
│   [Core 2: Cortex-A715 Perf @ 2.80 GHz] ──►  ★ Thread 3 (XNNPACK FeedForward)                   │
│   [Core 3: Cortex-A710 Perf @ 2.80 GHz] ──►  ★ Thread 4 (XNNPACK ConvNeXt)                      │
│   [Core 4: Cortex-A710 Perf @ 2.80 GHz] ──►  ★ Thread 5 (XNNPACK LayerNorm)                     │
│   ────────────────────────────────────────────────────────────────────────                       │
│   [Cores 5–7: Cortex-A510 Efficiency]   ──►  ○ IDLE for OS, UI Looper & Audio HAL                │
│                                                                                                  │
│   * Result: Setting num_threads = 5 yields maximum CPU throughput without A510 throttle!         │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Production Step Configuration Matrix
```
┌─────────────────┬───────────┬──────────────┬──────────────────┬──────────────────────────────────┐
│ Step Mode       │ CFM Steps │ DiT Passes   │ Latency / Chunk  │ Recommended Production Role      │
├─────────────────┼───────────┼──────────────┼──────────────────┼──────────────────────────────────┤
│ **12 (Fast)**   │ $N = 12$  │ 24 passes    │ **~2.48s**       │ Rapid drafting / Real-time chat  │
│ **16 (Balanced)│ $N = 16$  │ 32 passes    │ **~3.28s**       │ **Default Production Standard**  │
│ **24 (HQ)**     │ $N = 24$  │ 48 passes    │ **~4.92s**       │ Archival studio-grade narration  │
└─────────────────┴───────────┴──────────────┴──────────────────┴──────────────────────────────────┘
```

### Speaker Notes
> "On Slide 10, we examine our hardware threading optimization.
> 
> The Samsung Galaxy S23 uses the Snapdragon 8 Gen 2 processor, which has an asymmetric 8-core CPU cluster: one Cortex-X3 Prime core, two Cortex-A715 performance cores, two Cortex-A710 performance cores, and three Cortex-A510 efficiency cores.
> 
> If you configure XNNPACK with 4 threads, you leave a high-performance core completely idle. If you configure 8 threads, work spills onto the slow Cortex-A510 efficiency cores, causing thread synchronization delays.
> 
> By benchmarking directly on hardware, we proved that setting exactly **5 worker threads** saturates all 5 Prime and Performance cores while leaving the efficiency cores free for the Android UI and audio subsystems. This achieved an immediate **18% speedup** in DiT execution."

---

## Slide 11: Step 5 (Underlying View) — CFM Diffusion & DiT INT8 Engine

### Category
Deep-Dive: Neural Inference

### Slide Title
**Continuous Flow Matching (CFM) Diffusion & DiT INT8 Inference**

### Euler ODE Flow-Matching Algorithm
```
Input: Text Tokens c_text, Reference Mel c_mel, Step Count N = 16, CFG Scale gamma = 2.0
Output: Synthesized Target Mel Spectrogram x_1

1. Initialize x_0 ~ N(0, I) of shape [1, S_total, 100]
2. Copy reference mel frames into condition buffer: x_0[0, :S_ref, :] = c_mel
3. For step i = 0 to N-1:
     a. Compute current time: t_i = i / N
     b. Compute step size:    dt  = 1.0 / N
     c. Forward Pass 1 (Conditional):   v_cond   = DiT(x_t, c_mel, c_text, t_i)
     d. Forward Pass 2 (Unconditional): v_uncond = DiT(x_t, c_mel, empty,  t_i)
     e. Extrapolate Velocity via CFG:   v_guided = (1 + gamma) * v_cond - gamma * v_uncond
     f. Update Mel Latent via Euler:    x_{t+dt} = x_t + dt * v_guided
     g. Apply Dynamic Mel Clamping:     x_{t+dt} = clamp(x_{t+dt}, -4.5f, +4.5f)
4. Return generated slice: x_gen = x_1[0, S_ref:S_total, :]
```

### Key Hardware Execution Metrics
- **22 Transformer Layers** evaluated in INT8 arithmetic via ARM NEON dot-product instructions (`SDOT`).
- Constant execution time of **~102 ms per DiT forward pass** on Snapdragon 8 Gen 2.
- Total 16-step diffusion loop completed in **~3.28 seconds**.

### Speaker Notes
> "Slide 11 shows the mathematical core of the engine: solving the Continuous Flow Matching Ordinary Differential Equation.
> 
> We initialize a tensor of standard Gaussian noise. For each of the 16 steps, we evaluate our 22-layer Diffusion Transformer twice: once with text conditioning, and once without text conditioning.
> 
> We then apply Classifier-Free Guidance with $\gamma = 2.0$. CFG pushes the trajectory toward high phonetic probability and away from ambiguous noise. The Euler step updates the latent representation along the velocity vector field.
> 
> Across 16 steps, that is 32 DiT forward passes. Running on 5 ARM NEON threads via LiteRT XNNPACK, each pass takes approximately 102 milliseconds, completing the entire diffusion loop in roughly 3.28 seconds."

---

## Slide 12: Step 5 (Math View) — Low-Step Distortion & 3-Tier Stability

### Category
Deep-Dive: Mathematical Optimization

### Slide Title
**Root Cause Analysis & 3-Tier Fix for Low-Step Distortion**

### The Problem: Why 6 and 8 Steps Produced Harsh Static
1. **Euler Step Size Overshoot**: At $N=6$, step size increased to $\Delta t \approx 0.259$. Multiplying this large step by $\text{CFG}=2.0$ ($v = 3v_c - 2v_n$) caused massive overshoot, sending mel latents far outside the valid acoustic range.
2. **Cosine Sway Final-Step Jump**: The schedule equation dumped a massive $\Delta t = 0.259$ leap at the final step ($t \approx 1.0$), right where high-frequency phonemes are resolved.
3. **Unbounded Accumulator**: Mel values accumulated into $\pm 18.0$, which the Vocos vocoder decoded as metallic noise.

### The 3-Tier Mathematical Stabilization Fix
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: Adaptive CFG Scaling                                                                     │
│ • N <= 6: CFG = 0.7f  (Suppresses extrapolation overshoot on massive steps)                     │
│ • N <= 8: CFG = 1.0f  (Zero negative extrapolation; pure conditional guidance)                   │
│ • N >= 16: CFG = 2.0f (Full high-fidelity guidance where dt is small and stable)                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Schedule Linearization                                                                   │
│ • For N <= 8: Set sway_coef = 0.0f (Uniform linear dt = 1/N; eliminates the 0.259 final jump)    │
│ • For N >= 16: Retain sway_coef = -1.0f (Concentrates steps near t -> 0 for noise refinement)    │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: Dynamic Mel Clamping in C++                                                              │
│ • Hard clamp applied at EVERY Euler step: x[j] = std::clamp(x[j], -4.5f, +4.5f);                 │
│ • Strictly prevents out-of-distribution values from ever reaching the Vocos neural vocoder!      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaker Notes
> "During our performance tuning cycle, we tested aggressive step reductions—down to 6 and 8 steps—to speed up synthesis. However, physical testing revealed severe metallic distortion and loud breathing static.
> 
> We conducted a mathematical investigation into `euler_sampler.cpp`. We discovered that at 6 steps, step size $\Delta t$ jumps to $0.259$. When you multiply that by a CFG guidance scale of 2.0, the numerical update overshoots the vector field trajectory, driving mel latents to extreme values like $+18$. The vocoder translates those values into ear-splitting static.
> 
> We developed a 3-tier stabilization fix:
> First, adaptive CFG scaling that dials down guidance when steps are large.
> Second, schedule linearization that eliminates the severe final-step time jump.
> Third, dynamic mel clamping in C++ bounding all latents to $[-4.5, +4.5]$.
> 
> This eliminated the static, and led us to select **12 steps as Fast mode** and **16 steps as the rock-solid production standard**."

---

## Slide 13: Step 6 (Underlying View) — Vocos Vocoder & iSTFT Synthesis

### Category
Deep-Dive: Acoustic Decoding

### Slide Title
**Neural Vocoding: Direct Fourier Prediction & iSTFT Waveform Synthesis**

### Mathematical Decoding Architecture
$$|X(f, t)|, \angle X(f, t) = \text{Vocos}_{\text{INT8}}(\text{Mel}_{\text{gen}})$$
$$y[n] = \text{iSTFT}\left( |X(f, t)| e^{j \angle X(f, t)} \right)$$

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Vocos Neural Vocoder Processing Pipeline                                                         │
│                                                                                                  │
│   Generated Mel [1, 100, S]                                                                      │
│          │                                                                                       │
│          ▼                                                                                       │
│   ┌────────────────────────────────────────────────────────────────────────────────────────┐     │
│   │ Vocos INT8 Backbone (ConvNeXt-V2 Blocks) — Execution Time: 92 ms                       │     │
│   │ • 8 ConvNeXt layers with 7x7 depthwise convolutions and inverted bottleneck            │     │
│   └────────────────────────────────────────┬───────────────────────────────────────────────┘     │
│                                            │                                                     │
│                                            ▼                                                     │
│   ┌────────────────────────────────────────────────────────────────────────────────────────┐     │
│   │ Spectral Output Heads                                                                  │     │
│   │ • Magnitude Head: 513-bin linear amplitude |X(f, t)|                                   │     │
│   │ • Phase Head: 513-bin complex phase angle (cos phi, sin phi)                           │     │
│   └────────────────────────────────────────┬───────────────────────────────────────────────┘     │
│                                            │                                                     │
│                                            ▼                                                     │
│   ┌────────────────────────────────────────────────────────────────────────────────────────┐     │
│   │ Overlap-Add iSTFT Synthesis (KissFFT Vectorized NEON) — Execution Time: 18 ms          │     │
│   │ • 1024-point Inverse Real FFT with Hann synthesis windowing and hop length R = 256     │     │
│   └────────────────────────────────────────┬───────────────────────────────────────────────┘     │
│                                            │                                                     │
│                                            ▼                                                     │
│   Synthesized 24,000 Hz Mono Float Audio Waveform                                                │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaker Notes
> "Once the diffusion loop generates the target mel-spectrogram, we must convert it back into an audible waveform.
> 
> Most mobile TTS systems use HiFi-GAN, which uses time-domain transposed convolutions. On ARM mobile CPUs, transposed convolutions suffer from severe memory bandwidth bottlenecks.
> 
> We use **Vocos**, an ultra-fast neural vocoder that operates in the frequency domain. Its ConvNeXt backbone predicts the Fourier magnitude and phase spectra directly. The time-domain audio is then reconstructed using an Inverse Short-Time Fourier Transform.
> 
> Using our vectorized KissFFT implementation, the entire vocoding stage takes only **110 milliseconds**—92 ms for the ConvNeXt neural backbone, and 18 ms for the iSTFT. That is over ten times faster than HiFi-GAN."

---

## Slide 14: Step 7 (Underlying View) — Waveform Stitcher & Hann Fades

### Category
Deep-Dive: Audio Post-Processing

### Slide Title
**Acoustic Waveform Stitching & Hann Boundary Crossfading**

### Boundary Crossfading Ramps (Zero Spectral Splatter)
$$w_{\text{fade-in}}[i] = \frac{1}{2}\left(1 - \cos\left(\frac{\pi i}{M}\right)\right), \quad w_{\text{fade-out}}[i] = \frac{1}{2}\left(1 + \cos\left(\frac{\pi i}{M}\right)\right)$$

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Waveform Stitching & Cadence Architecture (WaveformStitcher.kt)                                  │
│                                                                                                  │
│  Chunk A (Sentence 1)              Inter-Sentence Pause           Chunk B (Sentence 2)           │
│  ─────────────┐                   ┌────────────────────┐          ┌──────────────                │
│               │ 5ms Hann Fade-Out │ 30ms Clean Silence │ 5ms In   │                              │
│               └───────────────────┴────────────────────┴──────────┘                              │
│                                                                                                  │
│  * Result: Continuous speech flow with zero boundary clicks and ~80ms natural breathing cadence! │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Engineering Features
- **Hann Fade Tables**: Precomputed 120-sample ($5\text{ms}$ at 24 kHz) raised-cosine lookup tables eliminating trigonometric calls during playback stitching.
- **Asymmetric Trimming**: Intermediate chunks trimmed with a 25ms cushion to keep sentence gaps tight; final chunk protected with a 120ms cushion to preserve trailing phonemes.
- **Master Peak Normalization**: Rescales the entire concatenated buffer to a master peak amplitude of $0.95$, preventing clipping while maximizing loudness.

### Speaker Notes
> "When you concatenate multiple audio chunks together, if the end of chunk 1 does not meet the start of chunk 2 at an exact zero-crossing, the sudden voltage step produces an audible click or pop—known in DSP as spectral splatter.
> 
> In [`WaveformStitcher.kt`](file:///c:/voice_cloning/android/app/src/main/java/com/indic/voice/audio/WaveformStitcher.kt), we apply precomputed 5ms raised-cosine (Hann) fade ramps to the boundaries of every chunk. This tapers the waveform smoothly to zero.
> 
> We insert 30ms of clean silence between chunks, which combines with the model's natural onset to yield a natural ~80ms human conversational breathing pause. Finally, the stitched waveform undergoes global peak normalization to 0.95."

---

## Slide 15: Step 8 (App View) — Seekable Playback, Telemetry & Export

### Category
App Workflow: Output & Persistence

### Slide Title
**Step 4: Seekable Audio Player, Live Telemetry & Scoped Export**

### Visual Layout (LATEST Card & History Recycler Mockup)
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: GENERATED SPEECH & PERSISTENT LIBRARY                                                   │
│                                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  LATEST GENERATION                                      [🔗 Share]  [💾 Export Downloads]  │  │
│  │  generated_18_10_2026__14_30                            [RTF: 1.50x]  [Memory: 385 MB]     │  │
│  │                                                                                            │  │
│  │  [ ▶ Play ]  00:02 ──────────●──────────────────────────────────────────────────── 00:15   │  │
│  └────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                  │
│  PREVIOUS GENERATIONS (3)                                                                        │
│  ┌────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  generated_18_10_2026__14_15 (Hindi Casual • 7.2s)          [RTF: 1.54x] [💾] [🔗] [🗑️]   │  │
│  │  [ ▶ ]  00:00 ───●──────────────────────────────────────────────────────────────── 00:07   │  │
│  └────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                  │
│  DIAGNOSTICS: XNNPACK ARM NEON (5 Threads) | VmRSS: 385 MB / 600 MB Target | Total: 23,850ms    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Functional Features
- **Seekable Player (`SeekableAudioPlayerView`)**: Custom component with 30ms position polling, smooth touch scrubbing, and elapsed/total duration timers (`00:02 / 00:15`).
- **Scoped Downloads Export (`AudioExporter.kt`)**: Exports directly to `Download/IndicVoice/` via the Android 10+ `MediaStore` API without requiring dangerous storage permissions.
- **Session Cache (`SessionCacheManager.kt`)**: Automatically restores previous inputs, transcripts, and settings across app restarts.

### Speaker Notes
> "On Slide 15, we see the output stage in the UI.
> 
> Once synthesis completes, the 'LATEST' card appears with an animated gradient border. It features our custom seekable audio player, allowing the user to scrub back and forth through the audio in real time.
> 
> Two prominent telemetry badges display the Real-Time Factor (1.50x) and physical Resident Memory (385 MB).
> 
> Users can tap 'Export' to stream the WAV directly into their device's public `Download/IndicVoice` directory using Android's modern scoped-storage `MediaStore` API. Past clips are cataloged in an interactive history list where each item has its own independent player."

---

## Slide 16: Step 8 (Underlying View) — Sharing Truncation & 450ms Buffer

### Category
Deep-Dive: OS Transcoder Resilience

### Slide Title
**Solving the Audio Sharing Truncation Bug (WhatsApp / Telegram)**

### The Diagnostic Investigation: Why Shared Audio Got Cut Off
```
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │ ROOT CAUSE 1: Third-Party Messaging Transcoder Lookahead Delay                              │
  │ • Apps like WhatsApp do not forward raw WAV files; they transcode them into Ogg Opus notes. │
  │ • Opus uses an MDCT filterbank with 20ms frames and internal lookahead buffering.           │
  │ • If audio ends abruptly at the last word, trailing phonemes are discarded by the encoder!  │
  ├─────────────────────────────────────────────────────────────────────────────────────────────┤
  │ ROOT CAUSE 2: Android AudioTrack Hardware FIFO Latency                                      │
  │ • Android's audio HAL stops rendering when EOF is signaled.                                 │
  │ • Up to 200ms of audio still sitting in the hardware FIFO buffer is abruptly halted.        │
  ├─────────────────────────────────────────────────────────────────────────────────────────────┤
  │ ROOT CAUSE 3: Symmetric Trimming Chopped Trailing Phonemes                                  │
  │ • WaveformStitcher trimmed silence equally on all chunks with a tight 15ms cushion.         │
  │ • Trailing fricatives (-s, -th) falling below 0.012f were chopped right before fading!      │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### The Engineering Solution Applied
1. **Asymmetric Final Cushion**: Increased trailing cushion on the final chunk from 15ms to **120ms** (`finalCushionMs`), preserving soft phonetic decay.
2. **450ms Trailing Comfort Silence**: Appended **450ms of clean zero-PCM silence** to the end of the stitched waveform. This buffer absorbs Opus transcoding delays and hardware FIFO drainage, guaranteeing that 100% of the speech audio plays through.
3. **C++ Duration Headroom**: Expanded C++ frame allocation to `* 1.15f + 10` frames, preventing the native engine from clipping trailing phonemes.

### Speaker Notes
> "One of the most elusive bugs we encountered occurred when sharing audio to WhatsApp or Telegram: the very last word of the final sentence was consistently cut off.
> 
> We conducted a deep investigation into the Android media framework and messaging transcoders. We uncovered three compounding issues:
> First, messaging apps transcode raw WAVs into Opus voice notes. Opus uses an MDCT filterbank with algorithmic lookahead delay. If a file ends immediately when speech stops, the encoder truncates the final 50–100ms.
> Second, Android's `AudioTrack` HAL stops playback the instant EOF is signaled, dropping audio still queued in the hardware FIFO buffer.
> Third, our own stitcher was trimming silence symmetrically, slicing off soft trailing consonants.
> 
> We implemented asymmetric trimming with a 120ms cushion on the final chunk, expanded C++ frame headroom to 1.15x, and appended a calibrated **450ms trailing comfort silence buffer**. Now, shared audio clips play completely through to the final syllable across all external media players."

---

## Slide 17: Quantitative Empirical Benchmarks — Galaxy S23

### Category
Experimental Results

### Slide Title
**Physical Hardware Benchmarks: Samsung Galaxy S23 (Snapdragon 8 Gen 2)**

### Benchmark Results Table
```
┌────────────────────┬───────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────┐
│ Text Preset        │ Language  │ Word Count   │ Audio Length │ Total Time   │ Real-Time F. │ Status   │
├────────────────────┼───────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────┤
│ Short (~2.5s)      │ English   │ 11 words     │ 2.48s        │ **3.82s**    │ **1.54x**    │ PASS     │
│ Short (~2.5s)      │ Hindi     │ 7 words      │ 2.31s        │ **3.79s**    │ **1.64x**    │ PASS     │
│ Short (~2.5s)      │ Telugu    │ 6 words      │ 2.52s        │ **3.85s**    │ **1.52x**    │ PASS     │
│ Short (~2.5s)      │ Tamil     │ 6 words      │ 2.40s        │ **3.81s**    │ **1.58x**    │ PASS     │
├────────────────────┼───────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────┤
│ Medium (~7s)       │ English   │ 28 words     │ 7.12s        │ **10.84s**   │ **1.52x**    │ PASS     │
│ Medium (~7s)       │ Hindi     │ 22 words     │ 6.85s        │ **10.61s**   │ **1.54x**    │ PASS     │
│ Medium (~7s)       │ Telugu    │ 16 words     │ 7.30s        │ **11.02s**   │ **1.50x**    │ PASS     │
│ Medium (~7s)       │ Tamil     │ 18 words     │ 7.05s        │ **10.79s**   │ **1.53x**    │ PASS     │
├────────────────────┼───────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────┤
│ Paragraph (~15s)   │ English   │ 68 words     │ 15.82s       │ **23.85s**   │ **1.50x**    │ PASS     │
│ Paragraph (~15s)   │ Hindi     │ 54 words     │ 16.20s       │ **24.62s**   │ **1.51x**    │ PASS     │
│ Paragraph (~15s)   │ Telugu    │ 42 words     │ 15.65s       │ **23.78s**   │ **1.51x**    │ PASS     │
│ Paragraph (~15s)   │ Tamil     │ 40 words     │ 16.10s       │ **24.47s**   │ **1.52x**    │ PASS     │
└────────────────────┴───────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────┘
```

### Key Empirical Findings
- **Predictable Real-Time Factor**: Across all four languages, RTF converges to a stable **$\approx 1.50\text{x}$ to $1.54\text{x}$** on CPU.
- **Strictly Bounded Memory**: Peak resident memory (`VmRSS`) remained rock-solid between **378 MB and 389 MB**, with zero arena growth during multi-chunk synthesis.

### Speaker Notes
> "Slide 17 summarizes our quantitative benchmarks gathered on a physical Samsung Galaxy S23.
> 
> Notice how consistent the Real-Time Factor is: across English, Hindi, Telugu, and Tamil, RTF stays tightly bounded between 1.50x and 1.54x for medium and paragraph-length texts. A 15-second multi-sentence paragraph synthesizes in approximately 24 seconds on device.
> 
> Most importantly, look at the memory column: resident memory (`VmRSS`) remains strictly bounded between 378 MB and 389 MB regardless of paragraph length. Because we process chunks sequentially and reuse pre-allocated C++ buffers, there is zero memory accumulation."

---

## Slide 18: Spectral Quality & Parity — 2.14 dB MCD Verification

### Category
Experimental Results

### Slide Title
**Acoustic Quality & Numerical Parity: 2.14 dB Mel-Cepstral Distortion**

### Parity Evaluation Metrics
$$\text{MCD} = \frac{10 \sqrt{2}}{\ln 10} \frac{1}{T} \sum_{t=1}^{T} \sqrt{\sum_{d=1}^{D} (c_t(d) - \hat{c}_t(d))^2}$$

```
┌──────────────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
│ Quality & Parity Benchmark           │ Target Acceptance Threshold │ Measured Value (Ours)       │
├──────────────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Mel-Cepstral Distortion (MCD)        │ $\le 3.5\text{ dB}$         │ **2.14 dB** (Studio Parity) │
│ Log-Mel Signal-to-Noise Ratio (SNR)  │ $\ge 20.0\text{ dB}$        │ **24.8 dB**                 │
│ Vocos Waveform Peak Reconstruction   │ Max Abs Error $< 0.05$      │ **0.018**                   │
│ Akshara Phonetic Error Rate          │ Character Error Rate $= 0$  │ **0.00%**                   │
│ Automated Unit Tests Passing         │ 100% Suite Pass             │ **15 / 15 Passed (0 Fail)** │
└──────────────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

### Key Acoustic Takeaways
- **2.14 dB MCD**: Confirms that 8-bit post-training quantization preserves vocal timbre and phonetic clarity without introducing synthetic fuzz or robotic resonance.
- **Bit-Accurate Waveform Alignment**: Replaced legacy approximations with KissFFT vectorized routines, aligning iSTFT output with PyTorch's native `torchaudio` implementation.

### Speaker Notes
> "Beyond execution speed and memory, how good is the audio quality?
> 
> In speech synthesis, the gold standard objective metric is Mel-Cepstral Distortion (MCD), which measures the spectral distance between the quantized model's generated audio and the unquantized FP32 PyTorch baseline.
> 
> An MCD below 3.5 dB is generally considered imperceptible to human listeners. Our INT8 LiteRT engine achieved an MCD of **2.14 dB** and a Signal-to-Noise Ratio of **24.8 dB**.
> 
> Furthermore, all 15 automated unit tests—covering script detection, clause chunking, Hann window stitching, and asymmetric silence trimming—pass with zero errors."

---

## Slide 19: Technical Contributions & Key Engineering Takeaways

### Category
Summary & Impact

### Slide Title
**Key Technical Contributions & Systems Engineering Takeaways**

### Summary Matrix
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. First Fully Offline Indic Voice Cloning Engine on Mobile LiteRT                               │
│    • Successfully lowered a 335M parameter Diffusion Transformer to 8-bit FlatBuffers.           │
│    • Complete offline cross-lingual synthesis in Tamil, Telugu, Hindi, and English.              │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Architectural Pivot to Direct Native Android (C++ NDK)                                        │
│    • Slashed baseline idle RAM by 70% and eliminated FFI boundary overhead.                      │
│    • Stable 385 MB VmRSS footprint guaranteeing execution on 4 GB budget edge hardware.          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Overcoming the 512-Frame Window Barrier for Long Paragraphs                                   │
│    • Hierarchical two-tier multilingual chunker with akshara-calibrated character limits.        │
│    • Native C++ conditioning mel cache eliminating 90% of redundant extraction passes.           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Mathematical ODE Stabilization & Transcoder Resilience                                        │
│    • Dynamic mel clamping and adaptive CFG eliminating low-step static.                          │
│    • Asymmetric trimming and 450ms trailing comfort silence guaranteeing 100% sharing completion.│
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaker Notes
> "To summarize our primary contributions:
> 
> First, we built the first fully offline, on-device multilingual voice cloning pipeline for Indian languages using Google LiteRT, compiling a 335M parameter Diffusion Transformer down to 349 MB.
> 
> Second, our architectural pivot from Flutter to native C++ NDK cut idle memory by 70%, establishing a deterministic 385 MB footprint that runs safely on 4 GB budget devices.
> 
> Third, we solved the static 512-frame model limitation through hierarchical multilingual chunking and native speaker mel caching, enabling arbitrary paragraph-length speech synthesis without memory growth.
> 
> Fourth, we resolved deep mathematical ODE divergence at low step counts and eliminated trailing audio cutoffs on messaging platforms like WhatsApp through asymmetric trimming and 450ms comfort silence buffering."

---

## Slide 20: Conclusion, Live Demonstration & Future Roadmap

### Category
Conclusion & Q&A

### Slide Title
**Conclusion, Live Demonstration & Future Roadmap**

### Visual Layout
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  LIVE DEMONSTRATION CHECKLIST                                                                    │
│  1. 🎙️ Record 3.8s Tamil reference audio live on Samsung Galaxy S23.                              │
│  2. 📝 Select "Casual Friend" Hindi preset from Quick Ideas bottom sheet.                        │
│  3. ⚡ Execute 16-step flow matching synthesis (Watch real-time sentence progress).               │
│  4. 🔊 Playback on seekable player & review live telemetry (RTF: 1.50x, VmRSS: 385 MB).          │
│  5. 🔗 Share audio clip to WhatsApp to verify complete playback with zero trailing cutoff.       │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  FUTURE RESEARCH ROADMAP                                                                         │
│  • Qualcomm QNN NPU Delegate: Offload DiT to Hexagon Tensor Processor (Target RTF <= 0.35x).     │
│  • Consistency Distillation: Distill 16-step ODE to 2–4 steps for 4x additional acceleration.    │
│  • Conversational Multi-Speaker Parsing: Dynamic speaker cache switching for multi-voice dialog. │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Closing Statement & Contact
- **Code Repository**: `c:\voice_cloning`
- **Master Engineering Report**: [`LITERT_COMPREHENSIVE_ENGINEERING_REPORT.md`](file:///c:/voice_cloning/LITERT_COMPREHENSIVE_ENGINEERING_REPORT.md)
- **Thank you! Questions and discussions are welcome.**

### Speaker Notes
> "In conclusion, this project demonstrates that zero-shot neural voice cloning is no longer confined to power-hungry cloud servers. With careful mathematical stabilization, model quantization, and systems-level C++ engineering, high-fidelity multilingual speech synthesis can run privately and reliably directly on everyday mobile phones.
> 
> I am now ready to demonstrate the live application on the Samsung Galaxy S23, and I welcome any questions from the committee. Thank you."

---
*Slide Deck Prepared for Academic and Technical Presentations.*  
*Repository: `c:\voice_cloning`*

