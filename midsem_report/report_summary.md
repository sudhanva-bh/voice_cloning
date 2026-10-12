# Report Summary — On-Device Multilingual Voice Cloning

**Project:** CS F377 Design Project — Mid-Semester Report  
**Student:** Sudhanva B H (2024A7PS0085H)  
**Supervisor:** Dr. Jabez Christopher, BITS-Pilani Hyderabad Campus  
**Co-Supervisor:** Reshma A.S., BITS-Pilani Hyderabad Campus

---

## Abstract Overview

This project engineers the **first fully offline, zero-shot multilingual voice cloning system for Indian languages**, designed to run entirely on budget Android edge hardware (Lenovo Tab K10 — MediaTek Helio P22T, 4 GB RAM, no NPU) without transmitting any user audio to remote servers.

---

## Core Problem

Three constraints form an unsolved intersection — the **Tri-Factor Challenge**:

| Pillar | Challenge |
|---|---|
| **Native Indic Language Support** | 1.4B speakers; existing edge models support only English/Chinese |
| **True Zero-Shot Voice Cloning** | Speaker adaptation from a 3–5 second clip, no model fine-tuning |
| **Strict Edge Execution** | < 1.5 GB RAM, no GPU, offline-only, no OOM crashes |

No existing system satisfies all three simultaneously.

---

## Architecture: Dual-Engine Pipeline

### Engine 1 — English Baseline (ZipVoice-Distill)
- **Model:** 123M parameter non-autoregressive Zipformer
- **Quantization:** INT8 ONNX → **104 MB**
- **Vocoder:** Vocos 24 kHz (54 MB)
- **Runtime:** `sherpa-onnx` C++ / Flutter Dart Isolate
- **Status:** ✅ Deployed and benchmarked on physical Android devices

### Engine 2 — Indic Multilingual Engine (IndicF5)
- **Model:** 22-layer Diffusion Transformer (DiT), 335M parameters
- **Pretrained on:** 1,417 hours of multi-speaker speech across 11 Indian languages (IndicVoices corpus, AI4Bharat)
- **Inference:** 8-step Euler ODE solver with CFG (γ = 2.0) and Sway Sampling (ρ = −1.0)
- **Vocoder:** INT8 Vocos — **22 MB** (Fourier iSTFT synthesis, ~10× faster than HiFi-GAN on ARM)
- **Quantization:** Static INT8 ONNX → **349 MB** (74% size reduction from 1.35 GB FP32)
- **Status:** ✅ Verified in Python; C++ NDK engine and Flutter FFI wiring in progress

---

## Key Engineering Milestones

| Iteration | Achievement |
|---|---|
| **1** | English ZipVoice baseline validated; RTF ≈ 0.35 on desktop |
| **2** | Flutter Android app with background Dart Isolate, FFmpeg transcoding |
| **3** | Multi-device benchmarks across 4 Android silicon tiers; confirmed Fixed Overhead Anomaly |
| **4** | IndicF5 PyTorch baseline verified across Tamil, Telugu, Kannada, Hindi |
| **5** | **Tail Hallucination Fix**: Calibrated syllabic duration model → 6.5 mel frames/character (~55 ms/char) |
| **6** | **Spatial Alignment Law**: Reference audio must be 3.5–5.0 seconds; longer clips cause attention collapse |
| **7** | Batch synthesis engine with warm RAM caching; 120-phrase multilingual dataset curated |
| **8** | Unified Voice Studio CLI package with TUI, catalog, and batch runner |
| **9** | Full INT8 ONNX export pipeline; DiT → 349 MB, Vocos → 22 MB |
| **10** | Native C++ engine with ONNX Runtime Mobile, pre-allocated static arenas, and Dart FFI bridge |

---

## Critical Technical Discoveries

### 1. Syllabic Duration Model
The naive English heuristic (15 mel frames/character) over-allocated duration for Indic text by ~2.5×, causing **tail hallucinations** (breathing, babble, repeated syllables). The calibrated formula:

```
T_gen = floor( len(w_tgt) × (6.5 / speed) ) frames
```

Matches the natural Indic speaking cadence of ~55 ms/Unicode character at a 256-sample hop size.

### 2. Spatial Text-Mel Alignment Law
When reference audio exceeds ~5.0 seconds, text conditioning for the target utterance falls outside the self-attention window, producing **unintelligible noise**. Established operational law: **3.5 ≤ Δt_ref ≤ 5.0 seconds**.

### 3. Memory Budget Comparison

| Component | FP32 Baseline | Quantized (Ours) |
|---|---|---|
| DiT Backbone | 1,350 MB | 349 MB (INT8 static) |
| Vocos Vocoder | 54 MB | 22 MB (INT8) |
| Inference Arenas | 850 MB (dynamic heap) | 280 MB (pre-allocated) |
| Flutter/Dart UI | 150 MB | 150 MB |
| **Total Peak RSS** | **2,404 MB — CRASH** | **801 MB — SAFE** |

Android LowMemoryKiller ceiling on 4 GB devices: ~1,500–1,800 MB. The quantized system leaves **+699 MB safety headroom**.

---

## Future Roadmap (Post-Midsem)

1. **Google LiteRT Migration** — Direct PyTorch → FlatBuffer via `litert-torch`
2. **NPU Acceleration** — Qualcomm QNN HTP and MediaTek NeuroPilot via `CompiledModel` API
3. **2-Step Consistency Distillation** (FlashSpeech) — Reduce ODE solver from 8 → 2 steps
4. **Zero-Copy AHardwareBuffer Pipelines** — Eliminate memcpy between DiT, Vocos, and AudioTrack
5. **Lenovo Tab K10 Physical Benchmarks** — Validate RSS < 850 MB, zero LMK terminations

---

## Report Changes Applied (October 2026)

| File | Change |
|---|---|
| `Chapters/Chapter1.tex` | Rewrote Section 1.1 from dry historical survey → compelling problem-first narrative with real-world use cases. Fixed LaTeX bug where `\section{}` was fused onto the same paragraph line. |
| `main.tex` | Added missing `\listoffigures` page. Replaced `treatise` → `report` in the abstract. |
| `Chapters/Chapter6.tex` | Enhanced conclusion with democratization framing. Replaced prose "immediate horizon" → prioritized numbered action list. |
