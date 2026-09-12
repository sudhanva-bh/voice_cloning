# On-Device Multilingual Voice Cloning & TTS Pipeline

Zero-shot, on-device neural voice cloning and text-to-speech (TTS) supporting **Tamil, Telugu, Hindi, Kannada, English, and 7 other Indian languages**.

---

## 📌 Project Architecture Overview

The system is structured as a **dual-engine pipeline**:

1. **English Engine (ZipVoice-Distill)**:
   - **Backbone**: Non-autoregressive Zipformer (~123M parameters).
   - **Quantization**: INT8 ONNX (~104 MB).
   - **Vocoder**: Vocos 24kHz ONNX (~54 MB).
   - **Runtime**: `sherpa-onnx` C++ / Dart bindings.
   - **Status**: Integrated & running inside Flutter app (`voice_clone_proto/`) and Python (`english_tts.py`).

2. **Indic Engine (IndicF5)**:
   - **Backbone**: Diffusion Transformer (DiT, 22 layers, ~335M parameters).
   - **Base Weights**: `model.safetensors` (1.35 GB PyTorch baseline).
   - **Vocoder**: Vocos 24kHz Neural Vocoder (Inverse STFT).
   - **Acoustic / Prosodic Conditioning**: Syllabic akshara duration estimation (~6.5 mel frames / character).
   - **Runtime**: Continuous Flow Matching (CFM) Euler ODE solver.
   - **Status**: Verified in Python CLI & batch benchmark suite. ONNX INT8 dynamic export and C++ NDK FFI bridge are in active development.

---

## 📂 Repository Structure

```
c:\voice_cloning\
├── pyproject.toml                           # Modern build & dependency configuration
├── README.md                                # Root documentation & execution guide
├── project_summary.md                       # Comprehensive architecture & technical summary
│
├── main.py                                  # Primary CLI & Interactive Studio entry point
├── clone.py                                 # Single-utterance IndicF5 voice cloning tool
├── batch.py                                 # Multilingual customizable batch synthesis tool
├── english_tts.py                           # English ZipVoice zero-shot TTS tool
│
├── src/
│   └── voice_studio/                        # Core modular Python package
│       ├── config.py                        # Central configuration & paths
│       ├── audio/                           # Audio I/O, format conversion & probing
│       │   └── io.py                        # WAV/MP3/OGG/FLAC serialization & RMS normalization
│       ├── catalog/                         # Voice catalog management
│       │   └── manager.py                   # voices.json CRUD & automatic audio ingestion
│       ├── dataset/                         # Phrases dataset manager
│       │   └── prompts.py                   # prompts.json loader & multi-select range parser
│       ├── engines/                         # Neural synthesis engines
│       │   ├── indicf5.py                   # IndicF5 DiT + CFM + Vocos inference pipeline
│       │   ├── batch_indicf5.py             # Batch engine with RAM reuse & multiprocessing
│       │   └── zipvoice.py                  # Sherpa-ONNX English ZipVoice engine
│       └── cli/                             # CLI interface & interactive TUI
│           ├── app.py                       # Argparse router
│           ├── interactive.py               # Interactive menu shell
│           └── commands.py                  # Subcommand action handlers
│
├── models/
│   └── indicf5/                             # IndicF5 checkpoints, vocab, and ONNX models
│       ├── model.safetensors                # PyTorch base weights (1.35 GB)
│       ├── vocab.txt                        # Multilingual character/token vocabulary (11.3 KB)
│       ├── indicf5_dit_int8_static.onnx     # Static INT8 ONNX DiT graph (~349 MB)
│       ├── indicf5_dit_dynamic_fp32.onnx    # Dynamic FP32 ONNX DiT graph (~1.36 GB)
│       └── indicf5_vocos_int8.onnx          # INT8 Vocos Neural Vocoder (~22 MB)
├── sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/ # Packaged English INT8 ONNX models
├── vocos_24khz.onnx                         # 24kHz Vocos Vocoder ONNX model (~54 MB)
├── samples/                                 # Speaker reference audio clips (.wav, .ogg, .mp3)
│   ├── voices.json                          # Registered reference voices catalog
│   ├── added/                               # Ingested user recordings
│   └── tamil_voices/                        # Tamil studio recordings
├── prompts.json                             # 120 authentic conversational phrases (Telugu, Tamil, Hindi)
├── generated/                               # Output synthesized audio files & batches
├── voice_clone_proto/                       # Flutter Android Application
├── reports/                                 # Progress reports, timeline & milestone notes
└── research_papers/                         # Literature & citations
```

---

## ⚙️ Environment Setup & Activation

First, activate the pre-configured Python virtual environment:

### Windows (PowerShell)
```powershell
.\sherpa-env\Scripts\Activate.ps1
```

### Windows (Command Prompt `cmd.exe`)
```cmd
.\sherpa-env\Scripts\activate.bat
```

### Linux / macOS
```bash
source ./sherpa-env/bin/activate
```

---

## 🚀 Mainstream Backend Commands

Once the environment is activated, execute any of the following tools:

### 1. Unified Voice Studio CLI (`main.py`)

#### A. Interactive Menu Program:
```powershell
python main.py
```
*(Launches an interactive menu with options to list, add, inspect, test single synthesis, run batch benchmarks, and delete voices)*

#### B. Direct Subcommands:
```powershell
# 1. List all registered voices & audio health status:
python main.py list

# 2. Inspect voice details and transcript:
python main.py info deep_classic

# 3. Add & automatically move audio to samples/added/:
python main.py add `
  --audio "C:/path/to/my_recording.wav" `
  --key "kannada_male_expressive" `
  --transcript "ನಮಸ್ಕಾರ, ನಾನು ಈ ದಿನ உங்களுக்கு ఒక ముఖ్యమైన విషయాన్ని చెప్పాలనుకుంటున్నాను." `
  --desc "Male Kannada - Conversational & Clear" `
  --move

# 4. Browse available phrases dataset (Telugu, Tamil, Hindi):
python main.py prompts

# 5. Direct single voice cloning:
python main.py clone --voice deep_classic --text "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?" --format mp3

# 6. Customizable batch synthesis:
python main.py batch --voice deep_classic --lang "1 2" --tier "2-4" --count "1-3" --format mp3 --steps 8
```

---

### 2. Single-Utterance Voice Cloning (`clone.py`)

#### A. Using Preset Voices (Quick & Easy)
```powershell
# List available voice presets:
python clone.py --list-voices

# Synthesize using preset voice key:
python clone.py `
  --voice deep_classic `
  --text "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் இப்போது உங்கள் குரலில் பேசுகிறேன்." `
  --out "generated/tamil_sample.mp3" `
  --format mp3 `
  --steps 8
```

#### B. Using Custom Reference Audio + Transcript
```powershell
python clone.py `
  --ref "samples/sudhanva_short_ref.wav" `
  --ref-text "The quick brown fox jumps over the lazy dog." `
  --text "నమస్కారం, మీరు ఎలా ఉన్నారు? నేను ఇప్పుడు మీ గొంతుతో తెలుగు మాట్లాడుతున్నాను." `
  --out "generated/telugu_sample.wav" `
  --format wav `
  --steps 8
```

---

### 3. Customizable Multilingual Batch Synthesis (`batch.py`)

Synthesize conversational sentences from [prompts.json](file:///c:/voice_cloning/prompts.json) (120 sentences categorized by `short`, `medium`, `midlong`, and `long` in Telugu, Tamil, and Hindi). The model loads once into RAM, and files are saved into incrementing batch folders (`generated/batches/batch-1/`, `batch-2/`, etc.).

#### A. Telugu & Tamil, Medium + Mid-long + Long tiers, 1st to 3rd phrases as MP3:
```powershell
python batch.py `
  --voice deep_classic `
  --lang "1 2" `
  --tier "2-4" `
  --count "1-3" `
  --format mp3 `
  --steps 8
```

#### B. Tamil & Hindi, Short + Medium, specific phrase indices `1 2` as OGG:
```powershell
python batch.py `
  --voice sahasra_reference_short `
  --lang "2 3" `
  --tier "1 2" `
  --count "1 2" `
  --format ogg `
  --steps 8
```

#### C. List All Available Phrases in the Dataset:
```powershell
python batch.py --list-prompts
```

#### D. Parallel Multi-Worker Execution:
```powershell
python batch.py `
  --voice deep_classic `
  --lang "1" `
  --tier "1" `
  --count "2" `
  --parallel `
  --workers 2
```

---

### 4. English Zero-Shot Voice Cloning (`english_tts.py`)

Synthesize English speech cloned from a reference audio file using Sherpa-ONNX ZipVoice:

```powershell
python english_tts.py `
  --ref "samples/vamsi.ogg" `
  --text "Hello everyone, welcome to the on-device voice cloning system." `
  --format mp3
```

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
| **English Pipeline (ZipVoice)** | Deployed & Benchmarked | ✅ Fully working in Python (`english_tts.py`) and Flutter app | Optimize cold-load time |
| **IndicF5 PyTorch (Python)** | Verified | ✅ Working on PC via `clone.py`, `batch.py`, and `main.py` | Reduce ODE steps (4-8) for speed |
| **IndicF5 ONNX INT8 Quantization** | Quantized (349MB) | ⚠️ Static shape (128 frames) exported | Export dynamic-length INT8 graph |
| **Native C++ Engine (`.so`)** | In Progress | ⏳ C++ source / CMake build to be written | Implement ODE solver & Vocos in C++ |
| **Dual-Engine Flutter UI** | In Progress | ⏳ Only English ZipVoice currently wired in UI | Add language dropdown & FFI service |
| **Device Benchmarks** | Recorded for S23/M53 | ℹ️ Benchmarks were for English ZipVoice | Run on-device benchmarks for IndicF5 |
