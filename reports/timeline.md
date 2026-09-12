# On-Device Multilingual Voice Cloning — Comprehensive Project Timeline & Engineering Roadmap

**Project Goal**: Deliver an offline, real-time, zero-shot neural voice cloning mobile application supporting **Tamil and Indic languages** on Android edge hardware.

---

## 1. High-Level Timeline & Status Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     Master Development Roadmap                                          │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 [Phase 1: English Baseline (Python)] ──────────────────────────────────────────► [100% COMPLETED]
  • Model evaluation (<200M params): ZipVoice-Distill, Chatterbox, Kokoro
  • Implemented `zipvoice-tts.py` with Sherpa-ONNX runtime
  • Verified zero-shot speaker adaptation on reference audio samples

 [Phase 2: English Flutter Mobile App] ────────────────────────────────────────► [100% COMPLETED]
  • Built production Flutter app (`voice_clone_proto`)
  • Integrated Sherpa-ONNX C++ bindings in background Dart Isolates
  • Implemented live mic recorder, file picker, and automatic FFmpeg 24kHz WAV transcoding
  • Built interactive waveform player & multi-format export to Android Downloads
  • Empirical hardware benchmarks on Galaxy S23, Galaxy Tab S9 FE+, and Galaxy M53

 [Phase 3: IndicF5 Tamil Feasibility on PC & ONNX Export] ──────────────────────► [100% COMPLETED]
  • Implemented single-utterance CLI (`test_indicf5_clone.py`) & batch suite (`test_batch_indicf5.py`)
  • Formulated syllabic duration model for Indian scripts (~15 mel frames / akshara)
  • Verified zero-shot voice cloning quality in Tamil, Telugu, Kannada, and Hindi
  • Quantized 335M DiT to INT8 static ONNX (`indicf5_dit_int8_static.onnx` ~349 MB, 74% reduction)
  • Quantized Vocos vocoder to INT8 (`indicf5_vocos_int8.onnx` ~22 MB)

 [Phase 4: Native C++ Engine & ONNX Runtime Mobile FFI Layer] ──────────────────► [70% IN PROGRESS]
  • Porting Euler ODE Flow-Matching loop (16 steps -> 8/4 steps) to C++
  • Constructing pre-allocated static tensor arenas to eliminate runtime heap allocations
  • Developing clean C FFI boundary (`indicf5_c_api.h`) and Dart FFI bridge (`indicf5_service.dart`)
  • Android NDK CMake configuration targeting `arm64-v8a` with XNNPACK acceleration

 [Phase 5: Dual-Engine Flutter Integration & UI Polish] ────────────────────────► [UPCOMING]
  • Integrate `IndicF5Service` into `voice_clone_proto` alongside English `TtsService`
  • Build language selector UI (English / Tamil / Telugu / Kannada / Hindi)
  • Dynamic asset unpacker & memory management for IndicF5 ONNX models and `vocab.txt`
  • End-to-end integration testing on Android mobile devices

 [Phase 6: Target Hardware Benchmarking & Optimization] ────────────────────────► [UPCOMING]
  • Comprehensive RTF, Cold Load, and Peak RSS benchmarking across 4 hardware tiers
  • Validate sub-1.5 GB memory footprint on budget Lenovo Tab K10 (4 GB RAM, Helio P22T)
  • Step schedule optimization (8-step and 4-step Euler) and NPU delegate evaluation
```

---

## 2. Phase-by-Phase Detailed Breakdown

### Phase 1: English Distillation Baseline (Python)
* **Objective**: Evaluate state-of-the-art lightweight (<200M parameters) zero-shot voice cloning models and establish an empirical performance baseline in Python.
* **Key Tasks Completed**:
  - Researched candidate models: ZipVoice-Distill (123M), Chatterbox-Nano (110M), GPT-SoVITS (77M), Kokoro-82M.
  - Confirmed ZipVoice-Distill (INT8, ~104MB, Emilia-trained) as the only <200M model natively supported by Sherpa-ONNX.
  - Built [`zipvoice-tts.py`](file:///c:/voice_cloning/zipvoice-tts.py) using Sherpa-ONNX Python API with 4-step flow matching and Vocos 24kHz neural vocoder.
  - Verified zero-shot speaker adaptation using studio and WhatsApp voice recordings.
* **Deliverables**: `zipvoice-tts.py`, baseline audio clips in `generated/`.

---

### Phase 2: English Mobile Application via Sherpa-ONNX (Flutter)
* **Objective**: Build a complete, cross-platform Android mobile application capable of on-device zero-shot voice cloning.
* **Key Tasks Completed**:
  - Built the [`voice_clone_proto`](file:///c:/voice_cloning/voice_clone_proto) Flutter application with Material 3 dark design.
  - Created a guided 4-step workflow:
    1. *Step 1*: Reference transcript selection (pre-built phonetically rich pangrams or custom text).
    2. *Step 2*: Reference audio acquisition (live microphone recording via `record` or file picker).
    3. *Step 3*: Target text entry (quick idea presets categorized by Short, Medium, Long).
    4. *Step 4*: Generation & History with built-in interactive audio player widget.
  - Integrated `ffmpeg_kit_flutter_new_audio` to automatically transcode arbitrary audio formats into standardized 16-bit 24kHz mono PCM WAV.
  - Executed Sherpa-ONNX inference inside a background **Dart Isolate** to keep UI thread fluid at 60 FPS.
  - Implemented multi-format exporter (`.wav`, `.mp3`, `.ogg`, `.m4a`) saving directly to Android `/storage/emulated/0/Download`.
  - Measured baseline RTF and Peak RSS across **Samsung Galaxy S23, Galaxy Tab S9 FE+, and Galaxy M53**.
* **Deliverables**: Complete Flutter application source code under `voice_clone_proto/`, baseline benchmark table in presentation deck.

---

### Phase 3: IndicF5 Tamil/Multilingual Feasibility on PC & Model ONNX Export
* **Objective**: Overcome the language barrier by verifying AI4Bharat's IndicF5 model for Tamil on PC and quantizing it for mobile deployment.
* **Key Tasks Completed**:
  - Cloned and adapted IndicF5 repository under [`scratch/indicf5_repo/`](file:///c:/voice_cloning/scratch/indicf5_repo/).
  - Developed [`test_indicf5_clone.py`](file:///c:/voice_cloning/test_indicf5_clone.py) for single-utterance CLI testing.
  - Formulated **syllabic duration estimation**:
    $$\text{Target Mel Frames} = \text{Ref Mel Frames} + \left( \frac{15.0}{\text{speed}} \times \text{len(Indic Text)} \right) + \text{Padding Frames}$$
    This eliminated audio cutoffs and trailing silence caused by alphabetic duration mismatch.
  - Built [`test_batch_indicf5.py`](file:///c:/voice_cloning/test_batch_indicf5.py) supporting sequential in-memory and parallel multi-process batch synthesis across 10 graduated prompts in **Tamil** and **Telugu**.
  - **Exported & Quantized Model Pipeline** under [`models/indicf5/`](file:///c:/voice_cloning/models/indicf5/):
    - `indicf5_dit_int8_static.onnx` (**~349 MB**, down from 1.35 GB FP32 — **74% size reduction**).
    - `indicf5_vocos_int8.onnx` (**~22 MB**).
    - `vocab.txt` extracted for zero-dependency multilingual character tokenization.
* **Deliverables**: Working Python inference scripts, generated Tamil/Telugu audio samples in `generated/`, and full quantized ONNX model suite.

---

### Phase 4: Native C++ Engine & ONNX Runtime Mobile FFI Layer *(CURRENT MILESTONE)*
* **Objective**: Build the custom C++ execution layer and Dart FFI bindings to run IndicF5 on Android without Sherpa-ONNX dependency.
* **Current Status**: **70% Completed**
* **Tasks in Progress**:
  - Developing `indicf5_engine.cpp` with ONNX Runtime Mobile C++ API.
  - Implementing pre-allocated static memory arenas for tensor buffers to prevent Android OOM kills.
  - Writing native C++ Euler ODE integration loop ($x_{t+\Delta t} = x_t + \Delta t \cdot v_\theta$).
  - Implementing Vocos iSTFT vocoder decoding in C++.
  - Creating C API interface (`indicf5_c_api.h`) and Dart FFI wrapper (`indicf5_service.dart`).
  - Setting up Android NDK `CMakeLists.txt` targeting `arm64-v8a` with XNNPACK multi-threading.
* **Expected Completion Deliverables**: Compiled `libindicf5_engine.so` and functional Dart FFI service.

---

### Phase 5: Dual-Engine Flutter Integration & UI Polish *(UPCOMING)*
* **Objective**: Integrate IndicF5 into the Flutter app alongside ZipVoice to provide seamless English and Tamil/Indic voice cloning.
* **Planned Tasks**:
  - Add language selector dropdown in `HomeScreen` (English, Tamil, Telugu, Kannada, Hindi).
  - Implement dynamic engine routing:
    - *English* $\rightarrow$ `TtsService` (ZipVoice via Sherpa-ONNX).
    - *Tamil / Indic* $\rightarrow$ `IndicF5Service` (Custom ONNX Runtime C++ FFI).
  - Update `ModelLoader` to unpack `indicf5_dit_int8_static.onnx`, `indicf5_vocos_int8.onnx`, and `vocab.txt` to application support storage.
  - Expand prompt library with phonetically balanced Tamil reference pangrams and test phrases.
* **Deliverables**: Production-ready dual-engine Flutter APK.

---

### Phase 6: Target Hardware Benchmarking & Optimization *(UPCOMING)*
* **Objective**: Empirically evaluate and optimize the full system on real physical devices across multiple hardware tiers.
* **Planned Tasks**:
  - Run standardized benchmark protocol across:
    1. **Samsung Galaxy S23** (Snapdragon 8 Gen 2, 8 GB RAM)
    2. **Samsung Galaxy Tab S9 FE+** (Exynos 1380, 8 GB RAM)
    3. **Samsung Galaxy M53** (MediaTek Dimensity 900, 8 GB RAM)
    4. **Lenovo Tab K10** (MediaTek Helio P22T, 4 GB RAM)
  - Measure:
    - Real-Time Factor (RTF) across Short, Medium, Long text.
    - Peak RSS memory footprint (validating $<1.5\text{ GB}$ ceiling).
    - Cold-load and warm-load latency.
  - Test 8-step and 4-step Euler step reduction to optimize latency.
  - Final project presentation deck and technical documentation.

---

## 3. Hardware Test Matrix & Milestone Target Metrics

| Device Tier | Device Model | Processor / SoC | RAM | Target Engine | Target RTF | Peak RSS Target | Status |
|---|---|---|---|---|---|---|---|
| **Flagship** | Samsung Galaxy S23 | Snapdragon 8 Gen 2 | 8 GB | ZipVoice / IndicF5 | **< 0.5x** | < 1,000 MB | Baseline Tested |
| **Upper Mid-Range** | Galaxy Tab S9 FE+ | Exynos 1380 | 8 GB | ZipVoice / IndicF5 | **< 1.0x** | < 1,200 MB | Baseline Tested |
| **Mid-Range** | Galaxy M53 5G | Dimensity 900 | 8 GB | ZipVoice / IndicF5 | **< 1.2x** | < 1,200 MB | Baseline Tested |
| **Target Budget** | Lenovo Tab K10 | MediaTek Helio P22T | 4 GB | IndicF5 INT8 | **< 2.5x** | **< 850 MB (Strict)** | Upcoming Target |

---

## 4. Key Risks & Mitigation Matrix

| Identified Risk | Impact Level | Mitigation Strategy Implemented |
|---|---|---|
| **Android Out-Of-Memory (OOM) Kill on 4GB RAM devices** | **HIGH** | Quantized DiT to static INT8 (349 MB) and Vocos to INT8 (22 MB); pre-allocated static tensor arenas to eliminate dynamic runtime heap growth. |
| **High RTF Latency on CPU-only SoCs** | **HIGH** | Using multi-threaded XNNPACK ARM NEON execution provider; reducing Euler steps from 16 to 8 (and evaluating 4-step Reflow). |
| **Audio Cutoffs in Indian Languages** | **MEDIUM** | Formulated language-specific syllabic duration estimation (~15 mel frames per Indic akshara). |
| **Sherpa-ONNX Lack of DiT Support** | **MEDIUM** | Built custom native C++ engine (`libindicf5_engine.so`) linking directly to ONNX Runtime Mobile C++ API. |
