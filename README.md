# On-Device Multilingual Voice Cloning & TTS Pipeline

Zero-shot, on-device neural voice cloning and text-to-speech (TTS) supporting **English, Tamil, Telugu, Kannada, Hindi, and 7 other Indian languages**.

---

## 📌 Project Architecture Overview

The system is structured as a **dual-engine pipeline**:

1. **English Engine (ZipVoice-Distill)**:
   - **Backbone**: Non-autoregressive Zipformer (~123M parameters).
   - **Quantization**: INT8 ONNX (~104 MB).
   - **Vocoder**: Vocos 24kHz ONNX (~54 MB).
   - **Runtime**: `sherpa-onnx` C++ / Dart bindings.
   - **Status**: Integrated & running inside Flutter app (`voice_clone_proto/`) and Python (`zipvoice-tts.py`).

2. **Indic Engine (IndicF5)**:
   - **Backbone**: Diffusion Transformer (DiT, 22 layers, ~335M parameters).
   - **Base Weights**: `model.safetensors` (1.35 GB PyTorch baseline).
   - **Vocoder**: Vocos 24kHz Neural Vocoder (Inverse STFT).
   - **Acoustic / Prosodic Conditioning**: Syllabic akshara duration estimation (~15 mel frames / character).
   - **Runtime**: Continuous Flow Matching (CFM) Euler ODE solver.
   - **Status**: Verified in Python CLI & batch benchmark suite. ONNX INT8 dynamic export and C++ NDK FFI bridge are in active development.

---

## 📂 Repository Structure

```
c:\voice_cloning\
├── README.md                                # Root documentation & execution tutorial
├── project_summary.md                       # Comprehensive architecture & engineering summary
├── test_indicf5_clone.py                   # Single-utterance CLI voice cloning script (PyTorch/CFM)
├── test_batch_indicf5.py                   # Sequential & parallel batch benchmark suite
├── zipvoice-tts.py                         # Standalone Sherpa-ONNX English runner
├── models/
│   └── indicf5/                            # IndicF5 checkpoints, vocab, and ONNX models
│       ├── model.safetensors               # PyTorch base weights (1.35 GB)
│       ├── vocab.txt                       # Multilingual character/token vocabulary (11.3 KB)
│       ├── indicf5_dit_int8_static.onnx    # Static INT8 ONNX DiT graph (~349 MB)
│       ├── indicf5_dit_dynamic_fp32.onnx   # Dynamic FP32 ONNX DiT graph (~1.36 GB)
│       └── indicf5_vocos_int8.onnx         # INT8 Vocos Neural Vocoder (~22 MB)
├── sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/ # Packaged English INT8 ONNX models
├── vocos_24khz.onnx                        # 24kHz Vocos Vocoder ONNX model (~54 MB)
├── samples/                                # Speaker reference audio clips (.wav, .ogg, .m4a)
├── generated/                              # Output synthesized audio files (.wav)
├── scratch/indicf5_repo/                   # AI4Bharat IndicF5 source repository
├── voice_clone_proto/                      # Flutter Android Application
├── reports/                                # Progress reports, timeline & milestone notes
└── research_papers/                        # Downloaded literature & citations
```

---

## ⚙️ Prerequisites & Environment Setup

The backend relies on the pre-configured Python virtual environment located in `.\sherpa-env`.

### 1. Activate Environment (PowerShell)
```powershell
.\sherpa-env\Scripts\Activate.ps1
```
*Or execute directly with `.\sherpa-env\Scripts\python.exe` without activating.*

### 2. Verify Installed Packages
```powershell
.\sherpa-env\Scripts\python.exe -c "import torch, librosa, soundfile, vocos, sherpa_onnx, onnxruntime; print('Environment Verified successfully!')"
```

---

## 🚀 Backend Execution Tutorial

### 1. Run IndicF5 Voice Cloning (Single Utterance)

Run `test_indicf5_clone.py` to clone a speaker's voice into Tamil, Kannada, Telugu, or Hindi.

> 💡 **Tip for Laptop / CPU Execution**:
> On a CPU without CUDA, use `--steps 4` for quick testing (~30 seconds). Use `--steps 8` or `--steps 16` for higher phonetic fidelity.

#### A. Tamil Example
```powershell
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --ref "samples/sudhanva_voic_clone.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley." `
  --text "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் இப்போது உங்கள் குரலில் தமிழில் பேசுகிறேன்." `
  --out "generated/tamil_sample.wav" `
  --steps 4
```

#### B. Kannada Example
```powershell
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --ref "samples/sudhanva_voic_clone.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley." `
  --text "ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಾ? ನಾನು ಈಗ ನಿಮ್ಮ ಧ್ವನಿಯಲ್ಲಿ ಕನ್ನಡ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ." `
  --out "generated/kannada_sample.wav" `
  --steps 4
```

#### C. Telugu Example
```powershell
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --ref "samples/sudhanva_voic_clone.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley." `
  --text "నమస్కారం, మీరు ఎలా ఉన్నారు? నేను మీ గొంతులో తెలుగు మాట్లాడుతున్నాను." `
  --out "generated/telugu_sample.wav" `
  --steps 4
```

#### D. Hindi Example
```powershell
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --ref "samples/sudhanva_voic_clone.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley." `
  --text "नमस्ते, आप कैसे हैं? मैं अब आपकी आवाज़ में हिंदी बोल रहा हूँ।" `
  --out "generated/hindi_sample.wav" `
  --steps 4
```

#### CLI Parameters:
- `--ref`: Path to reference audio recording (16-bit 24kHz/48kHz WAV, OGG, or M4A).
- `--ref-text`: Exact transcript of the reference audio.
- `--text`: Target text in any supported Indic language.
- `--out`: Destination `.wav` filepath.
- `--steps`: Number of Euler ODE sampling steps (Default: `16`, recommended for fast CPU: `4` or `8`).
- `--cfg`: Classifier-Free Guidance scale (Default: `2.0`).
- `--speed`: Speech speed multiplier (Default: `1.0`).

---

### 2. Run Batch Benchmark Suite

To test multiple sentences of varying lengths (Short $\approx 4$ words to Very Long $\approx 28$ words) in **Tamil** and **Telugu**:

```powershell
# Sequential mode (reuses model in memory):
.\sherpa-env\Scripts\python.exe test_batch_indicf5.py --steps 4

# Parallel mode (multi-worker processes):
.\sherpa-env\Scripts\python.exe test_batch_indicf5.py --steps 4 --parallel --workers 2
```

---

### 3. Run English Baseline (ZipVoice via Sherpa-ONNX)

```powershell
.\sherpa-env\Scripts\python.exe zipvoice-tts.py
```
Outputs synthesized speech to `generated/<speaker_name>_<timestamp>.wav`.

---

## 📱 Running the Flutter Mobile App (`voice_clone_proto`)

1. Open a terminal in `voice_clone_proto/`:
   ```powershell
   cd voice_clone_proto
   ```
2. Install dependencies:
   ```powershell
   flutter pub get
   ```
3. Connect an Android device (with USB debugging enabled) and launch:
   ```powershell
   flutter run --release
   ```

---

## 📊 Reality Check & Current Project State

| Component | Documented Status | Actual State | Next Steps |
|---|---|---|---|
| **English Pipeline (ZipVoice)** | Deployed & Benchmarked | ✅ Fully working in Python and Flutter app | Optimize cold-load time |
| **IndicF5 PyTorch (Python)** | Verified | ✅ Working on PC via `test_indicf5_clone.py` | Reduce ODE steps (4-8) for speed |
| **IndicF5 ONNX INT8 Quantization** | Quantized (349MB) | ⚠️ Static shape (128 frames) exported | Export dynamic-length INT8 graph |
| **Native C++ Engine (`.so`)** | In Progress | ⏳ C++ source / CMake build to be written | Implement ODE solver & Vocos in C++ |
| **Dual-Engine Flutter UI** | In Progress | ⏳ Only English ZipVoice currently wired in UI | Add language dropdown & FFI service |
| **Device Benchmarks** | Recorded for S23/M53 | ℹ️ Benchmarks were for English ZipVoice | Run on-device benchmarks for IndicF5 |
