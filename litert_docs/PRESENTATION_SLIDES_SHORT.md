# On-Device Multilingual Voice Cloning: Condensed Slide Deck (14 Slides)

**Document Title**: Presentation Slide Deck (Condensed Version) — End-to-End App Workflow, Underlying Neural Architecture, and Edge Optimization  
**File**: `c:\voice_cloning\PRESENTATION_SLIDES_SHORT.md`  
**Parent Document**: [`PRESENTATION_SLIDES_WORKFLOW.md`](file:///c:/voice_cloning/PRESENTATION_SLIDES_WORKFLOW.md) (Full 20-Slide Version)  
**Target Duration**: 15–20 Minute Academic Defense / Technical Presentation  
**Target Hardware**: Android Mobile Devices (Snapdragon 8 Gen 2 / MediaTek Helio P22T)  
**Core Technologies**: Google LiteRT, IndicF5 (Diffusion Transformer), Vocos Neural Vocoder, C++20 NDK, Kotlin Coroutines, XNNPACK ARM NEON  

---

## Slide Index (14 Slides)

```
┌───────┬────────────────────────────────────────────────────────┬───────────────────────────────────────┐
│ Slide │ Slide Title                                            │ Focus & Perspectives                  │
├───────┼────────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 01    │ Title Slide: On-Device Multilingual Voice Cloning      │ Overview & Academic Metadata          │
│ 02    │ Motivation & The Tri-Factor Challenge in Edge Voice AI │ Indic Phonetics, Zero-Shot, Edge RAM  │
│ 03    │ Dual-Perspective Architecture Overview                 │ App Wizard vs. Underlying C++/LiteRT  │
│ 04    │ The Architectural Pivot: Native C++ NDK vs. Flutter    │ 70% RAM Reduction & Zero-Copy Buffers │
│ 05    │ Step 1 (Audio): Capture, DSP & Native Mel Caching      │ App Recording + C++ Filterbank Cache  │
│ 06    │ Step 2 (Text): Presets & 512-Frame Chunker Engine      │ Quick Ideas UI + Multilingual NLP     │
│ 07    │ Step 3 (Hardware): Core Tuning & Step Scaling          │ Snapdragon 8 Gen 2 + 12/16 Step Modes │
│ 08    │ Step 4 (Inference): CFM Diffusion & DiT INT8 Engine    │ 22-Layer Transformer + Euler ODE Loop │
│ 09    │ Step 4 (Stability): Low-Step Distortion & 3-Tier Fix   │ Adaptive CFG, Linear dt, Mel Clamping │
│ 10    │ Step 5 (Acoustics): Vocos Vocoder & Waveform Stitcher  │ Frequency-Domain iSTFT + Hann Fades   │
│ 11    │ Step 6 (Output & Share): Seekable UI & Transcoder Fix  │ Scoped MediaStore + 450ms Tail Buffer │
│ 12    │ Quantitative Benchmarks & Spectral Quality Parity      │ Galaxy S23 RTF, 385 MB RAM, 2.14dB MCD│
│ 13    │ Core Technical Contributions & Innovations             │ Systems, Neural & Acoustic Takeaways  │
│ 14    │ Conclusion, Live Demonstration & Future Roadmap        │ QNN NPU Target, Distillation, Q&A     │
└───────┴────────────────────────────────────────────────────────┴───────────────────────────────────────┘
```

---

## Slide 01: Title Slide

### Header
**On-Device Multilingual Voice Cloning & Zero-Shot Speech Synthesis**  
*Ultra-Low Latency Flow Matching with Google LiteRT on Mobile Hardware*

### Presenter & Metadata
- **Presenter**: Sudhanva B H
- **Academic Guidance**: Dr. Jabez Christopher
- **Institution**: BITS Pilani, Hyderabad Campus
- **Repository**: `c:\voice_cloning`
- **Target Languages**: Tamil (Native Primary), Telugu, Kannada, Hindi, English

### Visual Layout
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                  │
│       🎙️ 3–5s Reference Voice Clip  ───►  [ On-Device LiteRT INT8 ]                              │
│                                                          │                                       │
│       📝 Target Text (Indic / English) ──────────────────┘                                       │
│                                                          │                                       │
│                                                          ▼                                       │
│                                                🔊 Cloned Voice Audio                             │
│                                       (Zero Cloud • 385 MB RAM • RTF 1.5x)                       │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaker Notes
> "Good morning, respected committee members. Today, I am presenting our work on **On-Device Multilingual Voice Cloning using Google LiteRT**.
> 
> Voice cloning typically relies on power-hungry cloud servers running multi-billion parameter models. Our goal was fundamentally different: to achieve zero-shot voice cloning from just 3 to 5 seconds of reference audio, running completely offline and privately on commodity Android phones, with native support for Indian languages like Tamil, Telugu, and Hindi alongside English.
> 
> In this presentation, I will walk you step-by-step through both the user-facing workflow of our production native Android application, and the deep C++, digital signal processing, and neural flow-matching systems operating beneath the surface."

---

## Slide 02: Motivation & The Tri-Factor Challenge in Edge Voice AI

### Slide Title
**The Tri-Factor Challenge: Why Edge Voice Cloning is Hard**

### Visual Layout (Tri-Factor Balance Diagram)
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
- **1. Native Indic Linguistic Complexity**:
  - Indian languages are abugida scripts based on syllabic *aksharas* and vowel diacritics (*matras*).
  - Western TTS models (e.g., Kokoro, standard F5-TTS) lack native Indic tokenizers and fail completely.
- **2. Instant In-Context Zero-Shot Cloning**:
  - Must extract vocal timbre, pitch, and cadence from 3–5s of reference audio without multi-hour speaker fine-tuning.
  - Autoregressive models (e.g., XTTS-v2) are memory-heavy and prone to hallucination on short audio clips.
- **3. Strict Mobile Edge Constraints**:
  - Target hardware includes budget educational tablets (e.g., **Lenovo Tab K10**: MediaTek Helio P22T, 4 GB RAM, ~1.5 GB user-space limit before Android's `LowMemoryKiller` terminates the app).
  - Must maintain a deterministic memory footprint under 500 MB while delivering conversational real-time factors (RTF).

### Speaker Notes
> "On-device voice cloning for Indian languages sits at the intersection of three competing constraints.
> 
> First, linguistic complexity: Indian languages are non-Latin abugida scripts where characters represent full syllables rather than individual letters. Existing open-source edge models are predominantly English or Chinese.
> 
> Second, zero-shot transfer: We cannot spend 10 minutes fine-tuning weights for every new user. The model must ingest raw audio and immediately mimic the speaker's vocal identity in-context.
> 
> Third, hardware limits: Mass-market educational devices like the Lenovo Tab K10 have only 4 GB of total system RAM and low-power Cortex-A53 CPU cores. If our app exceeds 1.5 GB, Android terminates the process immediately. Our system addresses all three constraints simultaneously."

---

## Slide 03: Dual-Perspective Architecture Overview

### Slide Title
**System Architecture: User-Facing Wizard vs. Underlying Neural Engine**

### Visual Layout (Split View / Two-Track Architecture)
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FRONT-END: Native Android User Experience (Kotlin 4-Step Wizard UI)                              │
│                                                                                                  │
│   [ Step 1: Script ] ──► [ Step 2: Audio ] ──► [ Step 3: Text ] ──► [ Step 4: Player & Share ]   │
│   • Auto-expanding input • 24kHz AudioRecord   • Quick Ideas presets • Seekable Scrubbing Player │
│   • Example Scripts      • File Picker + Check • 12/16/24 Step Mode  • MediaStore & FileProvider │
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
- **Kotlin UI Wizard**: Step-by-step guidance, real-time hardware telemetry display (`VmRSS`, `RTF`), and one-tap sharing.
- **C++ NDK Engine**: Zero-allocation memory management, Continuous Flow Matching (CFM) ODE integration, and ARM NEON vectorized DSP.

### Speaker Notes
> "This slide illustrates the core dual-track architecture of our solution.
> 
> On the top track is the user experience: a clean, 4-step wizard interface built in Kotlin following Material 3 guidelines. It manages microphone recording, file validation, preset selection, dynamic progress streaming, and audio export.
> 
> On the bottom track is what happens beneath the surface in C++: raw audio is converted to a log-mel spectrogram, the speaker conditioning is cached in native memory, the text is chunked into phonetically balanced segments, and an 8-bit quantized Diffusion Transformer solves an Ordinary Differential Equation across 5 CPU cores. The audio is then vocoded via Vocos, stitched with Hann crossfades, padded with comfort silence, and played back."

---

## Slide 04: The Architectural Pivot — Native C++ NDK vs. Flutter

### Slide Title
**Systems Engineering: Why We Replaced Flutter with Native C++ NDK**

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
│ Safety Margin on 4GB Devices         │ Dangerously close to OOM    │ **>1,000 MB Safety Cushion**│
└──────────────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

### Key Bullet Points
- **The Memory Wall**: The Flutter engine, Dart VM, and platform channels consumed 150 MB before inference even started, leaving dangerously little safety margin on 4 GB devices.
- **Zero-Copy Memory**: In native C++, large tensor buffers ($512 \times 100$ floats) never cross a language barrier; they are mapped directly to LiteRT tensor memory via `TfLiteTensorData()`.
- **Eliminated Thread Contention**: Removed synchronization stutter between Dart's event loop and XNNPACK's ARM NEON thread pool.

### Speaker Notes
> "One of our most critical engineering decisions was pivoting away from Flutter.
> 
> Our early prototypes were built in Flutter. However, profiling on physical devices revealed that the Dart VM and Skia engine consumed 150 MB of baseline RAM. During 16-step flow matching, crossing the Dart-to-C++ FFI boundary 32 times per chunk introduced measurable thread contention and garbage collection pauses.
> 
> By rebuilding directly in native Android using Kotlin and C++20 NDK, we slashed idle memory from 150 MB down to 45 MB, reduced peak resident memory to an ultra-stable 385 MB, and completely eliminated data copying. This single decision made deployment on 4 GB budget tablets completely stable."

---

## Slide 05: Step 1 (Audio) — Capture, DSP & Native Mel Caching

### Slide Title
**Step 1 Workflow: Audio Capture, Log-Mel DSP & Native Speaker Caching**

### Visual Layout (App UX + Underlying DSP Pipeline)
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ APP VIEW: Step 2 Audio Capture Card                                                              │
│ • [🎙️ Record Audio] (Native 24kHz AudioRecord) or [📁 Upload File] (RIFF Header Validator)        │
│ • Ready State: Green checkmark, duration (3.82s), and embedded Seekable Preview Player           │
└───────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                │ PCM Float Array
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ UNDERLYING C++ DSP: 100-Channel Log-Mel Filterbank & Native Speaker Caching                      │
│                                                                                                  │
│   24 kHz PCM ──► [1024 FFT (Hop=256)] ──► [100 Triangular Mel Bins] ──► [RMS Normalization]      │
│                                                                                  │               │
│                                                                                  ▼               │
│   cached_ref_mel_ (Stored ONCE in C++ RAM) ◄─────────────────────────────────────┘               │
│   * Reused across ALL subsequent text chunks (0ms Mel latency on chunks 2, 3, 4... Zero drift!) │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Technical Details
- **DSP Specs**: 24 kHz mono sampling, 1024-point FFT window (42.6 ms), 256 hop length (10.6 ms), 100 triangular mel bins from 0 to 12,000 Hz with RMS normalization.
- **Native Mel Caching**: Reference audio mel features are extracted **once** via `setReferenceAudio()` and held in native RAM. Every subsequent sentence chunk reuses this cached memory with **0ms extraction latency**, saving 90% of preprocessing CPU cycles and guaranteeing zero speaker timbre drift.

### Speaker Notes
> "In Step 1, the user provides a 3 to 5 second voice sample. They can record live at 24 kHz or upload an existing file, which is validated for correct RIFF headers. The UI displays an embedded preview player so the user can verify their audio before continuing.
> 
> In C++, [`audio_processor.cpp`](file:///c:/voice_cloning/android/app/src/main/cpp/audio_processor.cpp) converts this raw PCM into a 100-channel log-mel spectrogram using a 1024-point FFT window and 256 hop length.
> 
> Crucially, we split our native C++ API into `setReferenceAudio()` and `synthesizeChunk()`. The speaker's mel features are extracted once and cached in native memory. When synthesizing a 5-sentence paragraph, sentences 2 through 5 reuse this cached conditioning with zero extraction latency, saving 90% of preprocessing CPU time and preventing timbre drift."

---

## Slide 06: Step 2 (Text) — Presets & 512-Frame Chunker Engine

### Slide Title
**Step 2 Workflow: Multilingual Presets & 512-Frame Text Chunker**

### The 512-Frame Problem vs. Hierarchical Chunker
```
  THE PROBLEM: Static 512-Frame Window Budget (5.46s Total Audio)
  ┌─────────────────────────────────────────────┬───────────────────────────────────────────────┐
  │ Reference Audio Conditioning (~3.8s / 356f) │ Remaining Target Speech Budget (1.66s / 156f) │
  └─────────────────────────────────────────────┴───────────────────────────────────────────────┘
  * Unchunked 60-word paragraph forced into 156 frames -> "Auctioneer Effect" (Speedup + Distortion)

  THE SOLUTION: Two-Tier Hierarchical Segmentation (MultilingualChunker.kt)
  Arbitrary Long Paragraph (e.g., 75 words)
         │
         ▼
  TIER 1: Terminal Sentence Punctuation Split ([. ! ? । ॥ \n]) (Protects "Dr.", "Mr.", "i.e.")
         │
         ▼
  TIER 2: Clause & Boundary Split (If chunk > 44 Indic / 60 English characters)
         │
         ▼
  Result: Safe, Phonetically Complete Chunks (Each cleanly fitting <= 280 mel frames)
```

### App UX & Presets
- **Quick Ideas BottomSheet**: Curated **Teacher** and **Casual Friend** persona presets across English, Hindi (हिंदी), Telugu (తెలుగు), and Tamil (தமிழ்).
- **Duration Badges**: Short (~2.5s), Medium (~7s), and full Paragraph (~15s) tiers.

### Speaker Notes
> "Next, Step 2 handles target text input. The user can type freely or choose from our Quick Ideas bottom sheet, which features Teacher and Casual Friend persona presets across English, Hindi, Telugu, and Tamil.
> 
> But beneath the surface lies a major systems challenge: our INT8 DiT FlatBuffer was compiled with a fixed sequence budget of 512 frames—about 5.46 seconds of total audio. If the reference audio is 3.8 seconds, only 1.66 seconds remain for target speech!
> 
> Previously, feeding a 60-word paragraph into the engine forced all 60 words into that 1.66-second window, causing the 'auctioneer effect'—audio that was comically fast-forwarded and garbled.
> 
> We solved this with `MultilingualChunker.kt`. It performs two-tier hierarchical segmentation: first on sentence boundaries, and then on clause boundaries, enforcing strict 44-character Indic and 60-character English budgets. Every chunk fits safely inside the model window."

---

## Slide 07: Step 3 (Hardware) — Core Tuning & Step Scaling

### Slide Title
**Step 3 Workflow: Snapdragon 8 Gen 2 Core Tuning & Step Scaling**

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

### Production Step Configuration Options
```
┌─────────────────┬───────────┬──────────────┬──────────────────┬──────────────────────────────────┐
│ Step Mode       │ CFM Steps │ DiT Passes   │ Latency / Chunk  │ Recommended Production Role      │
├─────────────────┼───────────┼──────────────┼──────────────────┼──────────────────────────────────┤
│ **12 (Fast)**   │ $N = 12$  │ 24 passes    │ **~2.48s**       │ 25% faster; rapid conversation   │
│ **16 (Balanced)│ $N = 16$  │ 32 passes    │ **~3.28s**       │ **Default Production Standard**  │
│ **24 (HQ)**     │ $N = 24$  │ 48 passes    │ **~4.92s**       │ Archival studio-grade narration  │
└─────────────────┴───────────┴──────────────┴──────────────────┴──────────────────────────────────┘
```

### Speaker Notes
> "On Slide 7, we examine hardware thread tuning.
> 
> The Samsung Galaxy S23 uses the Snapdragon 8 Gen 2 processor, featuring an asymmetric 8-core CPU cluster: one Cortex-X3 Prime core, two Cortex-A715 performance cores, two Cortex-A710 performance cores, and three Cortex-A510 efficiency cores.
> 
> If you configure XNNPACK with 4 threads, you leave a high-performance core completely idle. If you configure 8 threads, work spills onto the slow Cortex-A510 efficiency cores, causing thread synchronization stalls.
> 
> By benchmarking directly on hardware, we proved that setting exactly **5 worker threads** saturates all 5 Prime and Performance cores while leaving the efficiency cores free for the Android UI. This achieved an immediate **18% speedup**.
> 
> We expose three step options: 12 steps (Fast, 25% faster), 16 steps (Balanced, our crystal-clear default), and 24 steps (HQ)."

---

## Slide 08: Step 4 (Inference) — CFM Diffusion & DiT INT8 Engine

### Slide Title
**Step 4 Underlying: Continuous Flow Matching (CFM) & DiT INT8 Inference**

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
> "Slide 8 shows the mathematical core of the engine: solving the Continuous Flow Matching Ordinary Differential Equation.
> 
> We initialize a tensor of standard Gaussian noise. For each of the 16 steps, we evaluate our 22-layer Diffusion Transformer twice: once with text conditioning, and once without text conditioning.
> 
> We then apply Classifier-Free Guidance with $\gamma = 2.0$. CFG pushes the trajectory toward high phonetic probability and away from ambiguous noise. The Euler step updates the latent representation along the velocity vector field.
> 
> Across 16 steps, that is 32 DiT forward passes. Running on 5 ARM NEON threads via LiteRT XNNPACK, each pass takes approximately 102 milliseconds, completing the entire diffusion loop in roughly 3.28 seconds."

---

## Slide 09: Step 4 (Stability) — Low-Step Distortion & 3-Tier Fix

### Slide Title
**Mathematical Stabilization: Root Cause Analysis & 3-Tier Fix**

### The Problem: Why 6 and 8 Steps Produced Harsh Static
1. **Euler Step Size Overshoot**: At $N=6$, step size jumped to $\Delta t \approx 0.259$. Multiplying this by $\text{CFG}=2.0$ ($v = 3v_c - 2v_n$) caused massive overshoot, projecting mel latents far outside the valid acoustic manifold.
2. **Cosine Sway Final-Step Jump**: The schedule equation dumped a massive $\Delta t = 0.259$ leap at the final step ($t \approx 1.0$), right where high-frequency phonemes are resolved.
3. **Unbounded Accumulator**: Mel values accumulated into $\pm 18.0$, which the vocoder decoded as metallic noise.

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

## Slide 10: Step 5 (Acoustics) — Vocos Vocoder & Waveform Stitcher

### Slide Title
**Step 5 Underlying: Vocos Vocoder & Hann Waveform Stitching**

### Dual-Stage Acoustic Reconstruction Pipeline
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE A: Vocos Neural Vocoding (Execution Time: ~110 ms per chunk)                               │
│                                                                                                  │
│   Generated Mel [1, 100, S] ──► [ConvNeXt-V2 Backbone (92ms)] ──► [Complex Fourier Head]         │
│                                                                          │                       │
│                                                                          ▼                       │
│   24 kHz PCM Waveform ◄── [Windowed Overlap-Add iSTFT via KissFFT NEON (18ms)]                   │
│   * 10x faster than HiFi-GAN transposed convolutions on ARM CPU!                                 │
└───────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                │ Sequential Audio Chunks
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE B: Waveform Stitcher with Hann Boundary Crossfading (WaveformStitcher.kt)                  │
│                                                                                                  │
│  Chunk A (Sentence 1)              Inter-Sentence Pause           Chunk B (Sentence 2)           │
│  ─────────────┐                   ┌────────────────────┐          ┌──────────────                │
│               │ 5ms Hann Fade-Out │ 30ms Clean Silence │ 5ms In   │                              │
│               └───────────────────┴────────────────────┴──────────┘                              │
│                                                                                                  │
│  * Result: Continuous speech flow with zero boundary clicks and ~80ms natural breathing cadence! │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key DSP Features
- **Vocos**: Frequency-domain prediction of magnitude $|X(f, t)|$ and complex phase $(\cos \phi, \sin \phi)$, decoded via vectorized KissFFT iSTFT.
- **Waveform Stitcher**: Precomputed 5ms raised-cosine (Hann) fade ramps at chunk edges to eliminate spectral splatter clicks, 30ms clean silence insertion for natural ~80ms breathing pauses, and master peak normalization to 0.95.

### Speaker Notes
> "Once the diffusion loop finishes, we reconstruct audible sound in two stages.
> 
> First, **Vocos Neural Vocoding**: unlike HiFi-GAN which uses slow time-domain transposed convolutions, Vocos operates in the frequency domain. Its ConvNeXt backbone predicts Fourier magnitude and phase spectra in 92 ms, and our vectorized KissFFT iSTFT reconstructs the waveform in 18 ms. The entire vocoder takes only 110 ms—over ten times faster than HiFi-GAN.
> 
> Second, **Waveform Stitching**: concatenating raw audio chunks creates clicks at the boundaries. In [`WaveformStitcher.kt`](file:///c:/voice_cloning/android/app/src/main/java/com/indic/voice/audio/WaveformStitcher.kt), we apply precomputed 5ms raised-cosine (Hann) fade ramps to the edges of every chunk and insert 30ms of clean silence. This yields smooth transitions and a natural ~80ms human conversational cadence."

---

## Slide 11: Step 6 (Output & Share) — Seekable UI & Transcoder Fix

### Slide Title
**Step 6 Workflow: Seekable Player, Scoped Export & Sharing Fix**

### App Output UX vs. The Sharing Truncation Fix
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ APP VIEW: LATEST Output Card & History Recycler                                                  │
│ • Custom Seekable Player (30ms polling ticker, smooth touch scrubbing, elapsed/total timers)     │
│ • Real-Time Telemetry Badges: RTF Pill (1.50x) and Memory RSS Pill (385 MB)                      │
│ • Scoped-Storage MediaStore Export directly to Download/IndicVoice/ (Zero permissions required)   │
└───────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                │ Intent.ACTION_SEND
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ UNDERLYING FIX: WhatsApp / Telegram Sharing Truncation Bug                                       │
│                                                                                                  │
│  THE PROBLEM: Shared voice notes cut off the final word prematurely due to:                      │
│  1. Third-party messaging apps transcode WAV to Ogg Opus (MDCT 20ms frames + lookahead delay).   │
│  2. Android AudioTrack HAL abruptly halts playback on EOF, dropping hardware FIFO buffer audio. │
│  3. Symmetric silence trimming chopped soft trailing consonants (-s, -th) on the last chunk.    │
│                                                                                                  │
│  THE ENGINEERING FIX APPLIED:                                                                    │
│  • Asymmetric Final Cushion: Increased final chunk trailing cushion from 15ms to 120ms.          │
│  • 450ms Trailing Comfort Silence: Appended 450ms clean zero-PCM buffer to end of stitched WAV.  │
│  • C++ Duration Headroom: Expanded C++ frame allocation to 1.15x + 10 frames (~106ms).           │
│  * Result: 100% of speech audio plays through completely across all messaging apps and players!  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaker Notes
> "In Step 6, the user hears their synthesized audio. The 'LATEST' card features our custom seekable audio player with real-time scrubbing and telemetry badges displaying the Real-Time Factor (1.50x) and Resident Memory (385 MB). Users can export the audio directly to `Download/IndicVoice` via Android's scoped-storage `MediaStore` API.
> 
> However, we encountered an elusive bug when sharing audio to WhatsApp or Telegram: the very last word of the final sentence was consistently cut off!
> 
> We discovered that messaging apps transcode WAV to Opus, which uses an MDCT filterbank with lookahead delay. Furthermore, Android's `AudioTrack` HAL halts playback the instant EOF is signaled, dropping the final 150ms of audio queued in the hardware FIFO buffer.
> 
> We solved this by implementing asymmetric silence trimming—preserving 120ms on the final chunk—and appending a calibrated **450ms trailing comfort silence buffer**. Now, shared audio plays completely through to the final syllable on all messaging platforms."

---

## Slide 12: Quantitative Benchmarks & Spectral Quality Parity

### Slide Title
**Empirical Evaluation: Performance Benchmarks & Quality Parity**

### S23 Hardware Performance (16 Steps, 5 Threads)
```
┌────────────────────┬───────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────┐
│ Text Preset        │ Language  │ Word Count   │ Audio Length │ Total Time   │ Real-Time F. │ Status   │
├────────────────────┼───────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────┤
│ Short (~2.5s)      │ English   │ 11 words     │ 2.48s        │ **3.82s**    │ **1.54x**    │ PASS     │
│ Short (~2.5s)      │ Hindi     │ 7 words      │ 2.31s        │ **3.79s**    │ **1.64x**    │ PASS     │
│ Medium (~7s)       │ English   │ 28 words     │ 7.12s        │ **10.84s**   │ **1.52x**    │ PASS     │
│ Medium (~7s)       │ Tamil     │ 18 words     │ 7.05s        │ **10.79s**   │ **1.53x**    │ PASS     │
│ Paragraph (~15s)   │ English   │ 68 words     │ 15.82s       │ **23.85s**   │ **1.50x**    │ PASS     │
│ Paragraph (~15s)   │ Telugu    │ 42 words     │ 15.65s       │ **23.78s**   │ **1.51x**    │ PASS     │
└────────────────────┴───────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────┘
```

### Spectral Quality & Parity Metrics
```
┌──────────────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
│ Quality & Parity Benchmark           │ Target Acceptance Threshold │ Measured Value (Ours)       │
├──────────────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Mel-Cepstral Distortion (MCD)        │ $\le 3.5\text{ dB}$         │ **2.14 dB** (Studio Parity) │
│ Log-Mel Signal-to-Noise Ratio (SNR)  │ $\ge 20.0\text{ dB}$        │ **24.8 dB**                 │
│ Peak Memory Footprint (VmRSS)        │ $< 600\text{ MB}$           │ **385 MB** (Constant)       │
│ Automated Unit Tests Passing         │ 100% Suite Pass             │ **15 / 15 Passed (0 Fail)** │
└──────────────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

### Speaker Notes
> "Slide 12 summarizes our quantitative experimental results.
> 
> On the Samsung Galaxy S23, Real-Time Factor converges to a stable **1.50x to 1.54x** across English, Hindi, Telugu, and Tamil. A 15-second multi-sentence paragraph synthesizes in approximately 24 seconds on CPU.
> 
> Resident memory (`VmRSS`) remains strictly bounded at **~385 MB**, with zero arena growth during multi-chunk synthesis.
> 
> In terms of acoustic quality, our INT8 quantized model achieved a Mel-Cepstral Distortion of **2.14 dB** compared to the unquantized FP32 PyTorch baseline—well below the 3.5 dB human perception threshold—confirming studio-grade voice parity. All 15 unit tests pass with zero errors."

---

## Slide 13: Core Technical Contributions & Innovations

### Slide Title
**Summary of Technical Contributions & Key Engineering Takeaways**

### Four Pillar Summary Matrix
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. First Fully Offline Indic Voice Cloning Engine on Mobile LiteRT                               │
│    • Lowered a 335M parameter Diffusion Transformer to an INT8 FlatBuffer (349 MB).              │
│    • Full offline cross-lingual zero-shot cloning in Tamil, Telugu, Hindi, and English.          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Systems Optimization: Native C++ NDK & Snapdragon Core Affinity                               │
│    • Slashed baseline idle RAM by 70% and eliminated FFI marshalling latency.                    │
│    • Saturated 5 Snapdragon Prime/Perf cores with 5 worker threads, avoiding slow A510 throttle. │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Overcoming the Static Window Limit for Arbitrary Paragraphs                                   │
│    • Hierarchical multilingual chunker with akshara-calibrated character limits.                 │
│    • Native C++ conditioning mel cache eliminating 90% of redundant extraction passes.           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Mathematical ODE Stabilization & Transcoder Resilience                                        │
│    • Dynamic mel clamping and adaptive CFG eliminating low-step static.                          │
│    • Asymmetric trimming and 450ms trailing comfort buffer guaranteeing 100% sharing completion. │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Speaker Notes
> "To summarize our primary contributions:
> 
> First, we built the first fully offline, on-device multilingual voice cloning pipeline for Indian languages using Google LiteRT, compiling a 335M parameter Diffusion Transformer down to 349 MB.
> 
> Second, our architectural pivot to native C++ NDK cut idle memory by 70%, establishing a deterministic 385 MB footprint that runs safely on 4 GB budget devices.
> 
> Third, we solved the static 512-frame model limitation through hierarchical multilingual chunking and native speaker mel caching, enabling arbitrary paragraph-length speech synthesis without memory growth.
> 
> Fourth, we resolved deep mathematical ODE divergence at low step counts and eliminated trailing audio cutoffs on messaging platforms like WhatsApp through asymmetric trimming and 450ms comfort silence buffering."

---

## Slide 14: Conclusion, Live Demonstration & Future Roadmap

### Slide Title
**Conclusion, Live Demonstration & Future Roadmap**

### Visual Layout
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  LIVE DEMONSTRATION CHECKLIST                                                                    │
│  1. 🎙️ Record 3.8s Tamil reference voice clip live on Samsung Galaxy S23.                        │
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

### Closing Statement
- **Code Repository**: `c:\voice_cloning`
- **Master Engineering Report**: [`LITERT_COMPREHENSIVE_ENGINEERING_REPORT.md`](file:///c:/voice_cloning/LITERT_COMPREHENSIVE_ENGINEERING_REPORT.md)
- **Full 20-Slide Reference Deck**: [`PRESENTATION_SLIDES_WORKFLOW.md`](file:///c:/voice_cloning/PRESENTATION_SLIDES_WORKFLOW.md)
- **Thank you! Questions and discussions are welcome.**

### Speaker Notes
> "In conclusion, this project demonstrates that zero-shot neural voice cloning is no longer confined to power-hungry cloud servers. With careful mathematical stabilization, model quantization, and systems-level C++ engineering, high-fidelity multilingual speech synthesis can run privately and reliably directly on everyday mobile phones.
> 
> I am now ready to demonstrate the live application on the Samsung Galaxy S23, and I welcome any questions from the committee. Thank you."

---
*Slide Deck Prepared for Academic and Technical Presentations.*  
*Repository: `c:\voice_cloning`*

