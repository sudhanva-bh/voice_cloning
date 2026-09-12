# Research Papers & Technical Foundation for On-Device IndicF5 Voice Cloning

This directory contains the primary research literature that underpins the architecture, acceleration, and on-device deployment of zero-shot voice cloning models (specifically **IndicF5** and **ZipVoice**) for mobile Android devices.

---

## 📚 Downloaded Papers Directory

| # | Paper Title & File | Primary Focus | Key Takeaway for IndicF5 Integration |
|---|---|---|---|
| 1 | [**F5-TTS: Fairytaler that Fakes Fluent Speech**](file:///c:/voice_cloning/research_papers/F5_TTS_Fairytaler_Flow_Matching.pdf)<br>`F5_TTS_Fairytaler_Flow_Matching.pdf` | Core Backbone Architecture | Explains the Diffusion Transformer (DiT) backbone, Continuous Flow Matching (CFM), and text-mel concatenation without phoneme aligners. |
| 2 | [**Vocos: Neural Vocoder**](file:///c:/voice_cloning/research_papers/Vocos_Neural_Vocoder.pdf)<br>`Vocos_Neural_Vocoder.pdf` | Ultra-fast Neural Vocoder | Inverse STFT neural synthesis replacing HiFi-GAN; allows fast Fourier-based waveform generation on mobile CPU. |
| 3 | [**Flow Matching for Generative Modeling**](file:///c:/voice_cloning/research_papers/Flow_Matching_Generative_Modeling.pdf)<br>`Flow_Matching_Generative_Modeling.pdf` | Mathematical Foundation | The core ODE vector field theory enabling deterministic, straight trajectories between Gaussian noise and target speech mels. |
| 4 | [**Voicebox: Speech Generation at Scale**](file:///c:/voice_cloning/research_papers/Voicebox_Universal_Speech_Generation.pdf)<br>`Voicebox_Universal_Speech_Generation.pdf` | Flow-Matching Speech Origin | Foundational work demonstrating non-autoregressive flow-matching for zero-shot speaker adaptation and in-context voice cloning. |
| 5 | [**Matcha-TTS: Fast Conditional Flow Matching**](file:///c:/voice_cloning/research_papers/Matcha_TTS_Fast_Conditional_Flow_Matching.pdf)<br>`Matcha_TTS_Fast_Conditional_Flow_Matching.pdf` | Fast ODE & Edge TTS | Demonstrates ODE step reduction (Euler / Midpoint) to achieve real-time speech synthesis on resource-constrained hardware. |
| 6 | [**FlashSpeech: Efficient Zero-Shot Speech Synthesis**](file:///c:/voice_cloning/research_papers/FlashSpeech_Efficient_ZeroShot_Speech_Synthesis.pdf)<br>`FlashSpeech_Efficient_ZeroShot_Speech_Synthesis.pdf` | Step Distillation (1–2 steps) | Explains adversarial consistency training and flow distillation to slash inference steps from 16–32 down to 1–2 steps. |
| 7 | [**Flow Straight and Fast: Rectified Flow**](file:///c:/voice_cloning/research_papers/Flow_Straight_and_Fast_Rectified_Flow.pdf)<br>`Flow_Straight_and_Fast_Rectified_Flow.pdf` | Trajectory Straightening | Theoretical basis for "Reflow" — turning curved diffusion paths into straight lines so 4 Euler steps suffice. |
| 8 | [**E2 TTS: Fully Non-Autoregressive Zero-Shot TTS**](file:///c:/voice_cloning/research_papers/E2_TTS_NonAutoregressive_ZeroShot.pdf)<br>`E2_TTS_NonAutoregressive_ZeroShot.pdf` | Alignment-Free Zero-Shot | Companion architecture showing how DiT can learn duration and alignment implicitly across languages. |
| 9 | [**IndicVoices: Multilingual Indian Speech Dataset**](file:///c:/voice_cloning/research_papers/IndicVoices_Multilingual_Indian_Speech.pdf)<br>`IndicVoices_Multilingual_Indian_Speech.pdf` | Indic Training Data & Diversity | Details the 11 Indian language speech corpus (Tamil, Telugu, Hindi, etc.) that empowers IndicF5's native prosody. |

---

## 🔍 Detailed Paper Summaries & Integration Significance

### 1. F5-TTS: A Fairytaler that Fakes Fluent and Faithful Speech with Flow Matching
- **Authors**: Yushen Chen, Zhikang Niu, Ziyang Ma, et al. (2024)
- **ArXiv**: [2410.06885](https://arxiv.org/abs/2410.06885)
- **Core Architecture**:
  - Backbone: **DiT (Diffusion Transformer)** with ConvNeXt V2 blocks (22 layers, 1024 embedding dim, 16 attention heads).
  - Mel-spectrogram: 100-channel Vocos-style mel-spectrograms.
  - Duration modeling: Text is padded/expanded to target length and concatenated directly with the noisy mel conditioning along the time dimension.
- **Why It Matters for IndicF5 Integration**:
  - IndicF5 is the direct Indian-language adaptation of F5-TTS trained on 1,417 hours of Indic speech.
  - Because Sherpa-ONNX does not currently have built-in F5-TTS / IndicF5 C++ loaders, we must implement the **text padding + ODE integration loop** in our mobile runtime.

---

### 2. Vocos: Closing the Gap Between Neural Vocoders and Fourier-Based Audio Synthesis
- **Authors**: Hubert Siuzdak (2023)
- **ArXiv**: [2306.00814](https://arxiv.org/abs/2306.00814)
- **Core Architecture**:
  - Instead of predicting time-domain samples autoregressively or via complex multi-stage transposed convolutions (like HiFi-GAN), Vocos predicts **Fourier magnitude and phase spectra** directly and reconstructs the audio via **Inverse Short-Time Fourier Transform (iSTFT)**.
- **Why It Matters for Mobile / Android**:
  - Vocos is dramatically faster than HiFi-GAN on mobile CPUs (~10x faster).
  - We have already quantized Vocos to **`indicf5_vocos_int8.onnx` (~22 MB)**, allowing fast 24kHz waveform synthesis directly in ONNX Runtime Mobile.

---

### 3. Matcha-TTS & Flow Matching (Lipman et al., 2022 / Mehta et al., 2023)
- **ArXiv**: [2309.03199](https://arxiv.org/abs/2309.03199) & [2210.02747](https://arxiv.org/abs/2210.02747)
- **Core Insights**:
  - Flow matching learns vector fields that generate probability paths between a standard Gaussian base distribution $p_0$ and the target speech data distribution $p_1$.
  - Generating audio requires solving the initial value problem (IVP):
    $$\frac{dx_t}{dt} = v_\theta(x_t, t, c)$$
    using an **Euler solver** across discrete time steps $t \in [0, 1]$.
- **Why It Matters for Mobile Integration**:
  - The Euler update step:
    $$x_{t + \Delta t} = x_t + \Delta t \cdot v_\theta(x_t, t, \text{text}, \text{cond})$$
    is mathematically simple and easily implemented in C++ or Dart without heavy framework overhead.

---

### 4. Step Distillation & Fast Sampling (FlashSpeech & Rectified Flow)
- **ArXiv**: [2404.14700](https://arxiv.org/abs/2404.14700) & [2209.03003](https://arxiv.org/abs/2209.03003)
- **The Challenge**:
  - Baseline IndicF5 uses 16–32 Euler steps. On a mid-range phone (MediaTek Helio P22T or Dimensity 900), running 16 forward passes through a 335M model causes high latency (RTF > 2.0).
- **The Solution from the Literature**:
  - **Reflow / Distillation**: Training the model with Rectified Flow straightens trajectories so the ODE can be solved accurately in **4 Euler steps** (matching ZipVoice-Distill's 4 steps).
  - **Consistency Distillation (FlashSpeech)**: Maps noise to clean mels in **1–2 steps** via adversarial consistency losses.

---

## 🛠 IndicF5 vs. ZipVoice Integration Comparison

| Feature / Step | ZipVoice-Distill (English) | IndicF5 (Tamil / Indic) |
|---|---|---|
| **Sherpa-ONNX Support** | ✅ Built-in native C++ model config (`OfflineTtsZipVoiceModelConfig`) | ❌ Not implemented in sherpa-onnx; requires custom ONNX Runtime pipeline |
| **Model Size (INT8)** | ~104 MB (123M params) | ~349 MB (335M params) |
| **Vocoder** | Vocos 24kHz ONNX (~54 MB) | Vocos 24kHz INT8 ONNX (~22 MB) |
| **Phoneme / Text Handling** | `espeak-ng` Grapheme-to-Phoneme + Lexicon | Multilingual Character / Syllable Tokenizer (`vocab.txt`) |
| **Sampling Steps** | 4 steps (pre-distilled) | 16 steps (Euler) $\rightarrow$ Can be reduced to 8 or 4 |
| **Mobile Integration Strategy** | Direct `sherpa_onnx` Flutter package | **Custom C++/Dart FFI wrapper calling ONNX Runtime Mobile (`onnxruntime`)** |

---

## 🚀 Step-by-Step Guide for IndicF5 Flutter Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 IndicF5 Flutter On-Device Integration Architecture          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
           ┌───────────────────────────┴───────────────────────────┐
           ▼                                                       ▼
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│     1. Dart Frontend (`Flutter`)     │  │   2. Native C++ / FFI Layer       │
├──────────────────────────────────────┤  ├───────────────────────────────────┤
│ • UI Wizard (Input Tamil text & ref) │  │ • Load `indicf5_dit_int8.onnx`    │
│ • Audio recording & FFmpeg 24kHz     │  │ • Load `indicf5_vocos_int8.onnx`  │
│ • Tamil Syllabic Duration Calculator │  │ • Run Euler ODE Loop (8–16 steps) │
│ • Character Tokenizer (`vocab.txt`)  │  │ • Execute Vocos iSTFT vocoder     │
└──────────────────────────────────────┘  └───────────────────────────────────┘
                                       │
                                       ▼
                  ┌───────────────────────────────────────────┐
                  │       3. ONNX Runtime Mobile (Android)    │
                  ├───────────────────────────────────────────┤
                  │ • CPU (XNNPACK multi-threaded)            │
                  │ • Optional NPU: Qualcomm QNN / MediaTek   │
                  └───────────────────────────────────────────┘
```

1. **Tokenizer & Duration Modeling in Dart**:
   - Load `vocab.txt` into a Dart map.
   - Calculate target mel length: $\text{duration} = \text{ref\_len} + (\text{len(tamil\_text)} \times 15) + \text{buffer}$.
2. **Euler ODE Execution in C++ / Dart FFI**:
   - Initialize noise tensor $x_0 \sim \mathcal{N}(0, I)$ of shape `[1, 100, duration]`.
   - Loop $t = 0 \to 1$ with step size $dt = 1 / N$ ($N = 8 \text{ or } 16$):
     - Pass $[x_t, t, \text{text\_tokens}, \text{ref\_mel}]$ to `indicf5_dit_int8_static.onnx`.
     - Update $x_{t+dt} = x_t + dt \cdot v_\theta$.
3. **Vocos Neural Synthesis**:
   - Slice generated mel frames: $x_{\text{gen}} = x_1[:, \text{ref\_len}:]$.
   - Pass to `indicf5_vocos_int8.onnx` to generate 24kHz audio samples.
