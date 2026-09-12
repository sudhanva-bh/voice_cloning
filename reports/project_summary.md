# On-Device Multilingual Voice Cloning — Comprehensive Project Summary & Architecture Guide

**Document Version**: 3.0  
**Date**: September 2026  
**Repository**: `c:\voice_cloning`  
**Target Platform**: Android Mobile & Edge Devices (ARM64-v8a) + Windows/Linux PC Python Backend  
**Supported Languages**: Tamil (Primary Target), Telugu, Kannada, Hindi, and 7 other Indian languages + English  

---

## 1. Executive Summary & Current State

This repository houses the complete engineering pipeline for **on-device, zero-shot neural voice cloning and text-to-speech (TTS)**. The system clones an unseen speaker's voice from a short reference audio clip (3–6 seconds) and synthesizes speech in Indian languages (Tamil, Telugu, Kannada, Hindi, Malayalam, Marathi, Gujarati, Bengali, Punjabi, Odia, Assamese) as well as English.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Dual-Engine Architecture                                    │
├──────────────────────────────────────┬──────────────────────────────────────────────────────┤
│ Engine 1: ZipVoice-Distill (English) │ Engine 2: IndicF5 (Tamil & Indic Languages)          │
├──────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ • Backbone: Zipformer (123M params)  │ • Backbone: Diffusion Transformer DiT (335M params)  │
│ • Quantization: INT8 ONNX (~104 MB)  │ • Weights: Safetensors PyTorch (1.35 GB baseline)    │
│ • Vocoder: Vocos 24kHz ONNX (~54 MB) │ • Vocoder: Vocos 24kHz Neural Vocoder (Inverse STFT) │
│ • Steps: 4 Flow-Matching steps       │ • Steps: 8–16 Euler ODE Flow-Matching steps          │
│ • Runtime: Native Sherpa-ONNX        │ • Runtime: Python CFM Engine (PyTorch)               │
│ • Status: Fully Deployed in Flutter  │ • Status: Verified in Python CLI & Batch Engine;     │
│           Android Mobile Prototype   │           ONNX Dynamic Export & C++ FFI Roadmap Open │
└──────────────────────────────────────┴──────────────────────────────────────────────────────┘
```

### Component Status Matrix

| Component | Architecture / Model | Implemented In | Current Status |
|---|---|---|---|
| **English Voice Cloning** | ZipVoice-Distill (123M INT8) | Flutter (`voice_clone_proto`) & Python (`zipvoice-tts.py`) | ✅ **Completed & Deployed** |
| **Flutter Android App** | Material 3 Dark Wizard UI, FFmpegKit 24kHz transcoder, Isolate runner, Waveform player | `voice_clone_proto/` | ✅ **Completed (English Engine)** |
| **IndicF5 Python CLI** | DiT 22-Layer CFM + Vocos 24kHz | `test_indicf5_clone.py` | ✅ **Completed & Verified** (Tamil, Telugu, Kannada, Hindi) |
| **IndicF5 Batch Engine** | In-memory warm model reuse, auto-incrementing `batch-i` folders, real-time unbuffered logging | `test_batch_indicf5.py` | ✅ **Completed & Verified** |
| **Indic Syllabic Duration** | 6.5 mel frames / Unicode code point (~55ms per character) | Python Inference Pipelines | ✅ **Completed & Calibrated** |
| **Vocos INT8 Vocoder** | INT8 Quantized Vocos ONNX (~22 MB) | `models/indicf5/indicf5_vocos_int8.onnx` | ✅ **Exported** |
| **IndicF5 Dynamic INT8 ONNX**| DiT INT8 ONNX Graph with variable sequence dimensions | `models/indicf5/` | ⏳ **Upcoming / To Be Exported** (Current static ONNX is fixed at 128 frames) |
| **Native C++ Engine** | `libindicf5_engine.so` (ONNX Runtime Mobile C++ API) | Android NDK CMake | ⏳ **Planned Phase** |
| **Dart FFI Bridge** | `indicf5_service.dart` connecting Flutter to C++ | `voice_clone_proto/lib/services/` | ⏳ **Planned Phase** |
| **Dual-Engine Mobile UI** | Language dropdown routing English $\to$ ZipVoice, Indic $\to$ IndicF5 | `voice_clone_proto/lib/main.dart` | ⏳ **Planned Phase** |

---

## 2. Repository Directory & File Inventory

```
c:\voice_cloning\
│
├── README.md                                # Root documentation & execution tutorial
├── project_summary.md                       # Master architecture & engineering summary (this document)
├── add_voice.py                             # Interactive & CLI voice catalog manager (auto copies/moves to samples/added/)
├── test_indicf5_clone.py                   # Single-utterance CLI voice cloning script (PyTorch/CFM)
├── test_batch_indicf5.py                   # Sequential & parallel batch benchmark engine (auto `batch-i`)
├── zipvoice-tts.py                         # Standalone Sherpa-ONNX English runner
├── vocos_24khz.onnx                        # 24kHz Vocos Vocoder ONNX model (~54 MB)
├── gg.md                                   # Empirical benchmark notes & presentation drafts
├── Voice Cloning PPT.pdf                   # Slide deck summarizing architecture & benchmarks
│
├── models/
│   └── indicf5/                            # IndicF5 Model Checkpoints & ONNX Artifacts
│       ├── model.safetensors               # PyTorch base weights (1.35 GB, 335M parameters)
│       ├── vocab.txt                       # Multilingual character/token vocabulary (11.3 KB, 187 tokens)
│       ├── indicf5_vocos_int8.onnx         # INT8 Quantized Vocos Neural Vocoder (~22 MB)
│       ├── indicf5_dit_fp32_static.onnx    # FP32 static ONNX graph (1.36 GB, 128 frames)
│       ├── indicf5_dit_dynamic_fp32.onnx   # FP32 dynamic shape ONNX graph (1.36 GB)
│       └── indicf5_dit_int8_static.onnx    # INT8 Quantized static DiT ONNX graph (~349 MB, 128 frames)
│
├── sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/
│   ├── encoder.int8.onnx                  # INT8 ZipVoice encoder (~5.5 MB)
│   ├── decoder.int8.onnx                  # INT8 ZipVoice flow-matching decoder (~124 MB)
│   ├── tokens.txt                         # Phoneme / token mapping
│   ├── lexicon.txt                        # English/Chinese phoneme dictionary
│   └── espeak-ng-data/                    # Grapheme-to-phoneme rule tables
│
├── samples/                                # Reference Voice Audio Clips
│   ├── voices.json                         # Master JSON catalog mapping voice keys to transcripts & styles
│   ├── added/                              # User-registered voice files managed by add_voice.py
│   ├── tamil_voices/                       # Cleaned & renamed Tamil reference voices
│   │   ├── tamil_classic_pangram.mp3       # Female Tamil Classic Pangram (~5.0s)
│   │   ├── tamil_conversational.mp3        # Female Tamil Expressive (~5.5s)
│   │   ├── tamil_crisp.mp3                 # Female Tamil Crisp (~3.8s)
│   │   ├── male_tamil_classic_pangram.mp3  # Male Tamil Classic Pangram (~5.5s)
│   │   ├── male_tamil_conversational.mp3   # Male Tamil Expressive (~5.5s)
│   │   ├── male_tamil_crisp.mp3            # Male Tamil Crisp (~4.0s)
│   │   └── deep_classic.mp3                # Deep Voice Tamil Pangram (~6.0s)
│   ├── sudhanva_short_ref.wav             # Clean 3.8s reference clip ("The quick brown fox jumps over the lazy dog.")
│   └── sudhanva_voic_clone.wav / .m4a     # 10.8s studio English recording
│
├── generated/                              # Synthesized Audio Outputs
│   ├── batches/                            # Output directory for `test_batch_indicf5.py`
│   │   ├── batch-1/                        # Auto-incremented batch generation folders
│   │   └── ...
│   ├── telugu_fixed.wav                    # Telugu 8-step synthesis output (5.56s)
│   ├── kannada_fixed.wav                   # Kannada 8-step synthesis output (5.48s)
│   └── tamil_sample_native.wav             # Native Tamil synthesis output (6.31s)
│
├── scratch/
│   └── indicf5_repo/                      # AI4Bharat IndicF5 source repository (F5-TTS fork)
│       └── f5_tts/
│           ├── model/                     # CFM, DiT, ConvNeXt text encoder, and utilities
│           └── infer/                     # Official inference utilities & vocoder loaders
│
├── voice_clone_proto/                     # Production Flutter Android Mobile Application
│   ├── lib/
│   │   ├── main.dart                      # Material 3 wizard UI, state management & audio player
│   │   ├── services/
│   │   │   ├── tts_service.dart           # Sherpa-ONNX ZipVoice background Dart Isolate runner
│   │   │   ├── model_loader.dart          # Asset manager extracting ZipVoice ONNX & espeak data
│   │   │   ├── audio_converter.dart       # FFmpegKit 24kHz WAV mono PCM converter
│   │   │   └── recorder_service.dart      # Real-time microphone audio recorder
│   │   └── widgets/
│   │       └── audio_player_widget.dart   # Interactive seekable waveform audio player
│   ├── assets/zipvoice/                   # Packaged ZipVoice ONNX models, vocab, and espeak data
│   └── pubspec.yaml                       # Flutter dependencies
│
├── reports/                               # Technical Reports & Documentation Archive
│   ├── progress_report.md                 # Full literature review and theoretical formulations
│   ├── timeline.md                        # Milestone breakdown & hardware test matrices
│   └── project_summary.md                 # Mirrored architecture summary
│
└── research_papers/                       # Downloaded Research Literature (9 PDFs + README index)
```

---

## 3. Core Architectural Principles & Key Engineering Lessons

### A. IndicF5 Model Architecture
IndicF5 is a non-autoregressive speech generation model trained by AI4Bharat on **1,417 hours** of Indian speech across 11 languages (Tamil, Telugu, Kannada, Hindi, Malayalam, Marathi, Gujarati, Bengali, Punjabi, Odia, Assamese).

* **Diffusion Transformer (DiT)**: 22 layers, hidden dimension $D = 1024$, 16 attention heads, feed-forward multiplier 2, 4 ConvNeXt-V2 text embedding layers with Rotary Position Embeddings (RoPE). Total: **335M parameters**.
* **Mel-Spectrogram Target**: 100-channel log-mel spectrograms extracted with FFT window 1024, hop size 256, sampling rate 24,000 Hz.
* **Continuous Flow Matching (CFM)**: Models probability trajectories between standard Gaussian noise $x_0 \sim \mathcal{N}(0, I)$ and clean mel spectrogram $x_1$.
* **Euler ODE Sampling**:
  $$x_{t + \Delta t} = x_t + \Delta t \cdot \left[ (1 + \gamma) v_\theta(x_t, t, c) - \gamma v_\theta(x_t, t, \emptyset) \right]$$
  where $\gamma = 2.0$ is the Classifier-Free Guidance (CFG) scale and $N = 8$ or $16$ steps with `sway_sampling_coef = -1.0`.
* **Vocoder**: 24kHz **Vocos** neural vocoder predicting Fourier magnitude and phase decoded via Inverse Short-Time Fourier Transform (iSTFT).

```
 ┌──────────────────────────┐                                       ┌──────────────────────────┐
 │  Target Text             │                                       │  Reference Audio (WAV)   │
 │  (Tamil / Telugu / ...)  │                                       │  (24kHz Mono PCM)        │
 └────────────┬─────────────┘                                       └────────────┬─────────────┘
              │ Tokenize via `vocab.txt`                                         │ Mel Filterbank + RMS Norm
              ▼                                                                  ▼
 ┌──────────────────────────┐                                       ┌──────────────────────────┐
 │  Text Token Embedding    │                                       │  Reference Mel Frames    │
 │  [1, Seq_Len, 512]       │                                       │  [1, 100, Ref_Frames]    │
 └────────────┬─────────────┘                                       └────────────┬─────────────┘
              │                                                                  │
              └───────────────────────────────┬──────────────────────────────────┘
                                              ▼ Concatenation along Time Axis
                                ┌───────────────────────────┐
                                │ Condition Tensor [1, 100, │
                                │ Total_Duration_Frames]    │
                                └─────────────┬─────────────┘
                                              │
              ┌───────────────────────────────┴───────────────────────────────┐
              │                                                               │
              ▼                                                               ▼
 ┌──────────────────────────┐                                       ┌──────────────────────────┐
 │ Standard Gaussian Noise  │                                       │ Diffusion Transformer    │
 │ x_0 ~ N(0, I)            │ ────► [Euler ODE Step Loop] ◄───────  │ (DiT 22 Layers, 335M)    │
 │ [1, 100, Total_Frames]   │       8 Steps (sway = -1.0)           │ Computes vector field    │
 └──────────────────────────┘                                       └──────────────────────────┘
                                              │
                                              ▼ Sliced Generated Mel [1, 100, Gen_Frames]
                                ┌───────────────────────────┐
                                │ Vocos Neural Vocoder      │
                                │ (Inverse STFT Synthesis)  │
                                └─────────────┬─────────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │ Final 24kHz Audio Output  │
                                └───────────────────────────┘
```

---

### B. Critical Engineering Lessons & Fixes Applied

#### 1. Syllabic Duration Calibration (6.5 mel frames / Unicode code point)
* **The Problem**: In Indian languages, written text contains base consonants and combining diacritics (*matras*, *viramas*, *anusvaras*). An earlier formula multiplied `len(target_text) * 15.0`, which generated a 12.6-second duration for a 5.5-second sentence. This caused the model to speak the sentence in 5s and spend the remaining 7s producing **dead silence, muffled breathing, repeating syllables, and babbling**.
* **The Calibrated Formula**:
  $$\text{Gen Frames} = \text{int}\left( \text{len}(\text{target\_text}) \times \frac{6.5}{\text{speed}} \right)$$
  $$\text{Total Window Frames} = \text{Ref Frames} + \text{Gen Frames} + \text{Pad Frames}$$
  This perfectly aligns the output duration to natural spoken pace (~55ms per character).

#### 2. Spatial Text-Mel Alignment (Reference Audio Duration)
* **The Problem**: F5-TTS ConvNeXt text encoder places all tokens `[Ref Text + Target Text]` at indices $0 \dots N$ at the beginning of the sequence. If a 10.8s reference audio is used, the entire text finishes at index 228 (time $t = 1.6\text{s}$), while target audio generation starts at frame 1016 ($t = 10.8\text{s}$). The model was forced to synthesize audio in a region where text was 100% zero padding, causing gibberish.
* **The Solution**: Use a clean **3.5 to 5.0 second reference audio clip** (such as [samples/sudhanva_short_ref.wav](file:///c:/voice_cloning/samples/sudhanva_short_ref.wav), 3.8s) whose transcript matches 100%.

#### 3. Audio RMS Normalization & Step Tuning
* Added automatic `target_rms = 0.1` normalization to ensure proper acoustic energy in the mel conditioning.
* Tuned the ODE schedule to **8 steps with `sway_sampling_coef = -1.0`**, producing clear phoneme articulation in ~35–60s on CPU.

---

## 4. Backend Execution Tutorial

### A. Environment Verification
The environment is self-contained in `.\sherpa-env`:
```powershell
.\sherpa-env\Scripts\python.exe -c "import torch, librosa, soundfile, vocos, sherpa_onnx, onnxruntime; print('Environment OK')"
```

### B. Single-Utterance Voice Cloning (`test_indicf5_clone.py`)

#### 1. Tamil Synthesis (from Native Tamil Reference)
```powershell
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --ref "samples/tamil_voices/tamil1.mp3" `
  --ref-text "யாதும் ஊரே யாவரும் கேளிர் என்ற உயரிய சிந்தனை, உலகெங்கும் வாழும் மனிதர்களின் இதயங்களில் அன்பையும் அமைதியையும் விதைக்கட்டும்." `
  --text "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் இப்போது உங்கள் குரலில் தமிழில் பேசுகிறேன்." `
  --out "generated/tamil_sample_native.wav" `
  --steps 8
```

#### 2. Telugu Synthesis (from Clean English Reference)
```powershell
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --ref "samples/sudhanva_short_ref.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog." `
  --text "నమస్కారం, మీరు ఎలా ఉన్నారు? నేను ఇప్పుడు మీ గొంతుతో తెలుగు మాట్లాడుతున్నాను." `
  --out "generated/telugu_fixed.wav" `
  --steps 8
```

#### 3. Kannada Synthesis
```powershell
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --ref "samples/sudhanva_short_ref.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog." `
  --text "ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಾ? ನಾನು ಈಗ ನಿಮ್ಮ ಧ್ವನಿಯಲ್ಲಿ ಕನ್ನಡ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ." `
  --out "generated/kannada_fixed.wav" `
  --steps 8
```

---

### C. Batch Synthesis Engine (`test_batch_indicf5.py`)

The batch engine loads the 1.35 GB model **once** into RAM and synthesizes multiple prompts back-to-back without redundant disk I/O. Each run automatically creates the next incremental folder (`generated/batches/batch-1/`, `batch-2/`, etc.):

```powershell
# Run the 6-prompt benchmark (3 Telugu + 3 Tamil, 4s to 12s):
.\sherpa-env\Scripts\python.exe test_batch_indicf5.py `
  --ref "samples/sudhanva_short_ref.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog." `
  --steps 8
```

---

### D. English Baseline (`zipvoice-tts.py`)
```powershell
.\sherpa-env\Scripts\python.exe zipvoice-tts.py
```

---

## 5. Mobile Application Architecture (`voice_clone_proto`)

The mobile client is built in Flutter with a Material 3 dark aesthetic:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           4-Step Mobile Wizard Flow                             │
├───────────────────┬───────────────────┬───────────────────┬─────────────────────┤
│ Step 1: Reference │ Step 2: Reference │ Step 3: Target    │ Step 4: Generation  │
│    Transcript     │      Audio        │      Text         │      & History      │
├───────────────────┼───────────────────┼───────────────────┼─────────────────────┤
│ • Select pre-set  │ • Live microphone │ • Custom text     │ • Background Isolate│
│   pangram script  │   recording via   │   input box       │   inference         │
│   or custom text  │   `record`        │ • Presets by      │ • Waveform player   │
│ • Phonetic nuance │ • File picker     │   length (Short,  │ • Real-time RTF/RSS │
│   coverage        │ • Auto FFmpeg     │   Medium, Long)   │ • Multi-format      │
│                   │   24kHz WAV       │                   │   export to storage │
└───────────────────┴───────────────────┴───────────────────┴─────────────────────┘
```

1. **Audio Sanitization (`audio_converter.dart`)**: Uses `ffmpeg_kit_flutter_new_audio` to transcode any recording format (`.ogg`, `.mp3`, `.m4a`, `.wav`) to standard 16-bit 24kHz mono PCM WAV.
2. **Background Dart Isolate (`tts_service.dart`)**: Runs neural synthesis in a separate `Isolate.run()` worker thread to maintain 60 FPS UI responsiveness.
3. **Interactive Audio Player (`audio_player_widget.dart`)**: Seekable waveform scrubbers using `just_audio`.
4. **Direct Export**: Converts and exports audio to `/storage/emulated/0/Download` in `.wav`, `.mp3`, `.ogg`, or `.m4a`.

---

## 6. Empirical Hardware Benchmark Results

### English ZipVoice-Distill (Measured on Physical Android Devices)

| Device | SoC / Processor | RAM | NPU? | Text Length | RTF (Median) | Peak RSS (MB) | Cold Load |
|---|---|---|---|---|---|---|---|
| **Samsung Galaxy S23** | Snapdragon 8 Gen 2 | 8 GB | Yes | Short (~5 words) | **3.826** | 1,033 MB | ~1,200 ms |
| **Samsung Galaxy S23** | Snapdragon 8 Gen 2 | 8 GB | Yes | Medium (~25 words) | **1.520** | 1,287 MB | — |
| **Samsung Galaxy S23** | Snapdragon 8 Gen 2 | 8 GB | Yes | Long (~65 words) | **1.288** | **1,562 MB** | — |
| **Galaxy Tab S9 FE+** | Exynos 1380 | 8 GB | Yes | Short (~5 words) | **9.279** | 1,021 MB | ~2,100 ms |
| **Galaxy Tab S9 FE+** | Exynos 1380 | 8 GB | Yes | Medium (~25 words) | **2.918** | 1,491 MB | — |
| **Galaxy Tab S9 FE+** | Exynos 1380 | 8 GB | Yes | Long (~65 words) | **2.508** | **1,772 MB** | — |
| **Samsung Galaxy M53** | Dimensity 900 | 8 GB | Yes | Short (~5 words) | **8.415** | 1,021 MB | ~1,850 ms |
| **Samsung Galaxy M53** | Dimensity 900 | 8 GB | Yes | Medium (~25 words) | **2.782** | 1,219 MB | — |
| **Samsung Galaxy M53** | Dimensity 900 | 8 GB | Yes | Long (~65 words) | **2.531** | **1,539 MB** | — |

### IndicF5 PyTorch (Measured on Laptop CPU, 8 Euler Steps)

| Language | Text Length / Character Count | Audio Duration | Generation Time (CPU) | Real-Time Factor (RTF) |
|---|---|---|---|---|
| **Telugu** | Medium-Long (75 chars) | **5.56 s** | **38.56 s** | **6.94x** |
| **Kannada** | Medium-Long (75 chars) | **5.48 s** | **47.32 s** | **8.63x** |
| **Tamil (Native)** | Medium-Long (85 chars) | **6.31 s** | **63.76 s** | **10.10x** |
| **Telugu** | Very Long (155 chars) | **11.58 s** | **72.20 s** | **6.23x** |
| **Tamil** | Very Long (155 chars) | **12.77 s** | **76.29 s** | **5.98x** |

---

## 7. Next Steps & Technical Roadmap for Future Agents

To transition IndicF5 from PC Python execution to on-device Android execution:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Engineering Roadmap to Mobile                      │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ Phase                         │ Concrete Technical Tasks                    │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 1. Dynamic INT8 ONNX Export   │ • Export DiT with dynamic shape dimensions  │
│                               │   `[1, frames, 100]` and `[1, text_len]`    │
│                               │ • Quantize to INT8 via ONNX Runtime tools   │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 2. Native C++ Engine          │ • Build `indicf5_engine.cpp` with ONNX      │
│                               │   Runtime Mobile C++ SDK and XNNPACK        │
│                               │ • Implement 8-step Euler ODE loop in C++    │
│                               │ • Integrate Vocos iSTFT vocoder decoding    │
│                               │ • Compile `libindicf5_engine.so` (arm64-v8a)│
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 3. Dart FFI Mobile Bridge     │ • Create `indicf5_service.dart` with FFI    │
│                               │ • Unpack Indic ONNX models in `ModelLoader` │
│                               │ • Add Language dropdown in `main.dart`      │
│                               │ • Route: English $\to$ ZipVoice (Sherpa),   │
│                               │          Indic $\to$ IndicF5 (Custom FFI)   │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 4. Hardware Benchmarks & OOM  │ • Benchmark on physical Android devices     │
│    Validation                 │ • Validate Peak RSS < 1.5 GB memory limit   │
└───────────────────────────────┴─────────────────────────────────────────────┘
```
