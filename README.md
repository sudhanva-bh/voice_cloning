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

### 1. Unified Voice Studio CLI Program (`voice_cli.py`)

Manage reference voices, inspect transcripts, and test neural voice cloning directly from an interactive menu or command-line subcommands. New voices are automatically validated, analyzed, and moved/copied to `samples/added/` while updating `samples/voices.json`.

#### A. Interactive Menu Program:
```powershell
.\sherpa-env\Scripts\python.exe voice_cli.py
```
*(Provides an interactive menu with options to list, add, inspect, test single synthesis, run batch benchmarks, and delete voices)*

#### B. Command-Line Subcommands:
```powershell
# 1. List all voices & audio status:
.\sherpa-env\Scripts\python.exe voice_cli.py list

# 2. Inspect voice details and transcript:
.\sherpa-env\Scripts\python.exe voice_cli.py info deep_classic

# 3. Add & automatically move audio to samples/added/:
.\sherpa-env\Scripts\python.exe voice_cli.py add `
  --audio "C:/path/to/my_recording.wav" `
  --key "kannada_male_expressive" `
  --transcript "ನಮಸ್ಕಾರ, ನಾನು ಈ ದಿನ ನಿಮಗೆ ಒಂದು ಮುಖ್ಯವಾದ ವಿಷಯವನ್ನು ತಿಳಿಸಲು ಬಯಸುತ್ತೇನೆ." `
  --desc "Male Kannada - Conversational & Clear" `
  --move

# 4. Directly test synthesis with IndicF5 (saving as MP3, OGG, WAV, or FLAC):
.\sherpa-env\Scripts\python.exe voice_cli.py test deep_classic `
  --text "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?" `
  --format mp3

# 5. Browse 120 authentic conversational phrases (Telugu, Tamil, Hindi):
.\sherpa-env\Scripts\python.exe voice_cli.py prompts

# 6. Customizable batch synthesis (filter by language, length tier, count, format):
.\sherpa-env\Scripts\python.exe voice_cli.py batch deep_classic `
  --lang tamil `
  --tier short,medium `
  --count 2 `
  --format mp3 `
  --steps 8
```

---

### 2. Run IndicF5 Voice Cloning (Single Utterance)

Run `test_indicf5_clone.py` to clone a speaker's voice into Tamil, Kannada, Telugu, or Hindi.

Preset voices can be selected directly from `samples/voices.json` with `--voice <KEY>`, or listed with `--list-voices`. Output format can be chosen with `--format [wav|mp3|ogg|flac]`.

#### A. Using Preset Voices (Quick & Easy)
```powershell
# List all available presets:
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py --list-voices

# Synthesize using a preset voice (e.g. saving as MP3):
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --voice tamil_crisp `
  --text "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் இப்போது உங்கள் குரலில் தமிழில் பேசுகிறேன்." `
  --out "generated/tamil_sample.mp3" `
  --format mp3 `
  --steps 8
```

#### B. Using Custom Audio + Reference Transcript
```powershell
.\sherpa-env\Scripts\python.exe test_indicf5_clone.py `
  --ref "samples/sudhanva_short_ref.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog." `
  --text "నమస్కారం, మీరు ఎలా ఉన్నారు? నేను ఇప్పుడు మీ గొంతుతో తెలుగు మాట్లాడుతున్నాను." `
  --out "generated/telugu_sample.wav" `
  --format wav `
  --steps 8
```

---

### 3. Run Customizable Batch Voice Cloning (`test_batch_indicf5.py`)

Run `test_batch_indicf5.py` to synthesize phrases from [prompts.json](file:///c:/voice_cloning/prompts.json) (120 conversational sentences categorized by `short`, `medium`, `midlong`, and `long` in Telugu, Tamil, and Hindi). The model is loaded once into memory, and all outputs are saved into automatically incrementing directories (`generated/batches/batch-1/`, `batch-2/`, etc.).

#### A. Run Full Multilingual Matrix (1 per tier × 4 tiers × 3 languages = 12 files)
```powershell
.\sherpa-env\Scripts\python.exe test_batch_indicf5.py `
  --voice tamil_classic_pangram `
  --count 1 `
  --steps 8
```

#### B. Run Flexible Multi-Number / Multi-Language Selections
```powershell
# 1. Telugu & Tamil, Short + Medium + Mid-long tiers, 1st & 2nd phrases as MP3:
.\sherpa-env\Scripts\python.exe test_batch_indicf5.py `
  --voice deep_classic `
  --lang "1 2" `
  --tier "1 2 3" `
  --count "1 2" `
  --format mp3 `
  --steps 8

# 2. Tamil & Hindi, Medium + Mid-long + Long tiers, specific phrase indices 2, 3, 4 as OGG:
.\sherpa-env\Scripts\python.exe test_batch_indicf5.py `
  --voice sahasra_reference_short `
  --lang "2 3" `
  --tier "2 3 4" `
  --count "2 3 4" `
  --format ogg `
  --steps 8
```

#### C. List All Available Phrases in the Dataset
```powershell
.\sherpa-env\Scripts\python.exe test_batch_indicf5.py --list-prompts
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
