# Master Document Index and Technical Digest: Mid-Semester Project Report

**Project:** On-Device Indic Voice Cloning and Text-to-Speech Synthesis for Edge Architectures  
**Course:** CS F377 Design Project, BITS-Pilani Hyderabad Campus  
**Student:** Sudhanva B H (ID: 2024A7PS0085H)  
**Supervisor:** Prof. Dr. Jabez Christopher | **Co-Supervisor:** Reshma A.S.  
**Primary Target Platform:** Lenovo Tab K10 (MediaTek Helio P22T, 4 GB RAM, Android 11/12, no discrete NPU)  
**Compiled Document:** [main.pdf](file:///c:/voice_cloning/midsem_report/main.pdf) (~66 pages)

---

## Executive Summary for AI Agents

This index serves as a comprehensive, structured map of the entire LaTeX technical report located in `c:\voice_cloning\midsem_report`. Any AI agent working on this repository can read this document to understand the full theoretical foundation, architectural decisions, engineering iterations, mathematical proofs, and experimental datasets without parsing tens of thousands of lines of raw TeX files.

### Core Application Purpose and Untapped Domain
Commercial speech synthesis platforms (ElevenLabs, OpenAI Voice, Azure TTS) predominantly target cloud entertainment, media dubbing, and Western languages. They are economically and architecturally unusable in vernacular Indian public schools due to three barriers: continuous cloud GPU costs, absent rural internet connectivity, and teacher biometric privacy risks.

This project specifically targets two previously untapped educational domains:
1. **Government School Children**: Enabling foundational literacy and conceptual lessons in the familiar, trusted voice of their local classroom teacher. Educational psychology shows that young learners exhibit significantly higher cognitive engagement, retention, and comfort with a familiar voice rather than a generic synthetic voice.
2. **Visually Impaired (Blind) Students**: Providing accessible auditory learning for textbooks, questions, and explanations in their own teacher's voice, ensuring continuity between classroom instruction and independent study.
3. **Zero-Cost Edge Feasibility**: Running 100% offline on state-subsidized classroom tablets (Lenovo Tab K10) with zero cloud API fees, bounded within an 801 MB memory footprint that prevents the Android Linux kernel LowMemoryKiller (LMK) from crashing the process.

---

## Master Table of Contents

```
midsem_report/
├── main.tex                             # Root document harness, font setups, front matter, includes
├── variables.tex                        # Metadata: titles, supervisor, student credentials
├── Acronyms.tex                         # Nomenclature (50 glossaries/acronyms)
├── Thesis.cls                           # Academic monograph class definition
├── Chapters/
│   ├── Chapter1.tex                     # Introduction, Problem Formulation, Tri-Factor Challenge
│   ├── Chapter2.tex                     # Theoretical Foundations & Comprehensive Literature Survey
│   ├── Chapter3.tex                     # System Architecture & Algorithmic Formulation
│   ├── Chapter4.tex                     # Implementation Methodology & 10 Engineering Iterations
│   ├── Chapter5.tex                     # Strategic Future Roadmap: Google LiteRT & Hardware NPU
│   └── Chapter6.tex                     # Conclusion, Societal Impact & Research Priorities
├── Appendices/
│   ├── AppendixA.tex                    # Mathematical Derivations & Numerical Proofs
│   └── AppendixB.tex                    # Multilingual Phonetic Evaluation Prompts Dataset
└── report_summary.md                    # High-level executive briefing
```

---

## Detailed Section-by-Section Summaries

### Front Matter & Setup

* **[variables.tex](file:///c:/voice_cloning/midsem_report/variables.tex)**:
  Defines project metadata including course code (`CS F377`), course name (`Design Project`), student name (`Sudhanva B H`), ID (`2024A7PS0085H`), supervisor (`Prof. Dr. Jabez Christopher`), supervisor title (`Professor`), co-supervisor (`Reshma A.S.`), and thesis title (`On-Device Indic Voice Cloning and Text-to-Speech Synthesis for Edge Architectures`).

* **[main.tex](file:///c:/voice_cloning/midsem_report/main.tex)**:
  The master LaTeX root file. Loads `Thesis.cls`, configures `geometry`, `amsmath`, `algorithm`, `booktabs`, and sets up native Unicode font rendering for Indic scripts via `fontspec` using Windows system font `Nirmala UI` (`\indicfont`, `\telugufont`, `\tamilfont`). Houses the complete **Abstract** and customized **Acknowledgements**.

* **[Acronyms.tex](file:///c:/voice_cloning/midsem_report/Acronyms.tex)**:
  Contains 50 acronym declarations for LaTeX `glossaries`, including `\gls{cfm}` (Continuous Flow Matching), `\gls{dit}` (Diffusion Transformer), `\gls{rtf}` (Real-Time Factor), `\gls{rss}` (Resident Set Size), `\gls{lmk}` (LowMemoryKiller), `\gls{npu}` (Neural Processing Unit), `\gls{litert}` (Google LiteRT), `\gls{qnn}` (Qualcomm AI Engine Direct), and `\gls{istft}` (Inverse STFT).

---

### Chapter 1: Introduction and Problem Formulation
**Source File:** [Chapters/Chapter1.tex](file:///c:/voice_cloning/midsem_report/Chapters/Chapter1.tex) (Lines 1 to 156)

* **Section 1.1: Teacher-Voice Learning in Government Schools and Accessibility for Blind Students**:
  Establishes the societal motivation. Explains why familiar-voice learning in regional languages (Telugu, Tamil, Hindi) enhances foundational literacy in rural classrooms, and how visually impaired students depend on teacher-voiced audio for academic continuity. Highlights four systemic barriers: commercial neglect of vernacular public education, offline rural realities, strict hardware budgets, and teacher biometric privacy.
* **Section 1.1.1: Voice Identity, Pedagogical Trust, and Biometric Privacy**:
  Explains the zero-shot paradigm (3 to 5 second reference recording, zero fine-tuning). Identifies why uploading teacher voiceprints to commercial cloud APIs creates severe privacy and voice-harvesting risks.
* **Section 1.2: Evolution of Speech Synthesis Paradigms**:
  Historical progression across three generations: formant synthesis (metallic), concatenative synthesis (inflexible, large storage), and statistical parametric speech synthesis (SPSS). Followed by deep neural networks (Tacotron 2, FastSpeech, VITS, HiFi-GAN) and modern zero-shot in-context flow matching.
* **Section 1.3: The Zero-Shot In-Context Voice Cloning Paradigm**:
  Mathematical formulation of zero-shot conditional density $p(\mathbf{x}_{\text{tgt}} \mid \mathbf{w}_{\text{tgt}}, \mathbf{x}_{\text{ref}}, \mathbf{w}_{\text{ref}}; \theta)$. Compares static global speaker embeddings (d-vectors/x-vectors, which suffer from information bottlenecks) against continuous audio inpainting (Voicebox, E2 TTS, F5-TTS).
* **Section 1.4: Rationale for On-Device Edge Execution in Public Education**:
  The three operational pillars: (1) Biometric Data Privacy and Teacher Protection, (2) Reliable Offline Operation in Vernacular Classrooms, and (3) Elimination of Cloud Infrastructure Costs and per-character fees.
* **Section 1.5: The Tri-Factor Challenge in Educational Edge Deployment**:
  The unsolved three-way intersection: (1) Native Indic and Dravidian Phonological Support for State Curricula, (2) Zero-Shot In-Context Generalization from 3 to 5s classroom samples, and (3) Strict Physical Edge Memory and Compute Budgets on Subsidized Tablets.
* **Section 1.6: Embedded Hardware Constraints and Operating System Resource Envelopes**:
  Detailed hardware specification of the reference **Lenovo Tab K10** (MediaTek Helio P22T, 8x Cortex-A53, ARMv8-A NEON, zero NPU, 4 GB LPDDR4X RAM). Explains the **Linux Kernel LowMemoryKiller (LMK)**: Android disables swap-to-flash, capping user-space foreground process RSS to $\approx 1,500$ to $1,800$ MB before issuing an uncatchable `SIGKILL`.
* **Section 1.7: Evaluation Framework for Edge Speech Generative Systems**:
  Defines core metrics: Peak Resident Set Size ($\text{VmRSS}$), Storage Footprint ($\le 400$ MB target), Mean Opinion Score (MOS), Mel-Cepstral Distortion (MCD), and Real-Time Factor ($\text{RTF} = T_{\text{synthesis}} / T_{\text{audio}}$). Discovers and formulates the **Fixed Overhead Anomaly** where short sentences exhibit elevated RTF due to constant initialization latency ($T_{\text{init}} \approx 1.2$ s).
* **Section 1.8: Scope and Structural Organization of the Report**:
  Overview of Chapters 2 through 6 and Appendices A and B.

---

### Chapter 2: Theoretical Foundations and Comprehensive Literature Survey
**Source File:** [Chapters/Chapter2.tex](file:///c:/voice_cloning/midsem_report/Chapters/Chapter2.tex) (Lines 1 to 284)

* **Section 2.1: Taxonomy of Deep Generative Speech Architectures**:
  Examines four deep learning families:
  * *Autoregressive (AR)*: $O(T)$ forward passes, exposure bias, KV-cache memory escalation (e.g., XTTS-v2).
  * *VAEs & Normalizing Flows*: $O(1)$ forward passes, but Monotonic Alignment Search (MAS) fails in zero-shot cross-lingual transfer (e.g., VITS).
  * *Score-Based Diffusion*: Reverse-time Itô SDEs require 50 to 1,000 curved steps, causing excessive latency on mobile CPUs.
  * *Continuous Flow Matching (CFM)*: Straight deterministic probability trajectories governed by ODEs, enabling low-step execution.
* **Section 2.2: Continuous Normalizing Flows and Optimal Transport Flow Matching**:
  Formal mathematics of push-forward maps $\psi_t$, vector fields $\mathbf{v}_t$, and continuity equation $\partial p_t / \partial t + \nabla \cdot (p_t \mathbf{v}_t) = 0$. Derives Conditional Flow Matching (CFM) with optimal transport displacement interpolants $\psi_t(\mathbf{x}) = (1 - (1 - \sigma_{\text{min}})t)\mathbf{x}_0 + t\mathbf{x}_1$ with constant target vector field $\mathbf{u}_t(\mathbf{x} \mid \mathbf{x}_1) = \mathbf{x}_1 - (1 - \sigma_{\text{min}})\mathbf{x}_0$.
* **Section 2.3: Trajectory Straightening and Step Distillation for Edge Efficiency**:
  * *Rectified Flow / Reflow (Liu et al., 2022)*: Recursive training on synthetic flow-generated pairs $(\mathbf{x}_0, \mathbf{z}_1)$ untangles crossing trajectories, enabling 4-step Euler ODE solving.
  * *FlashSpeech / Consistency Distillation (Zhang et al., 2024)*: Enforces self-consistency $f_\theta(\mathbf{x}_{t_1}, t_1) = f_\theta(\mathbf{x}_{t_2}, t_2)$, collapsing generation into 1 to 2 steps.
* **Section 2.4: Indic Linguistic Phonetics and Acoustic Corpora**:
  * *Akshara Syllabic Structure*: Orthographic syllable $C_0^k V$ with combining matras, viramas, and samyuktaksharas.
  * *IndicVoices Analysis*: 1,417 hours across 22 languages; akshara acoustic duration $\Delta t_{\text{akshara}} \approx 150$ to $220$ ms. At 24 kHz and hop size 256 ($\Delta t_{\text{frame}} \approx 10.67$ ms), each Unicode character maps to 5.5 to 7.0 mel frames.
  * *IndicF5 (AI4Bharat, 2025)*: Analysis of the *Phir Hera Fairy* paper (Praveen et al.). Proves that fine-tuning an English F5-TTS prior exclusively on Indic data yields superior cross-lingual zero-shot cloning without phonetic dictionaries.
* **Section 2.5: Edge Machine Learning Runtimes**:
  Comparative analysis of Sherpa-ONNX (fast for Zipformer/VITS, lacks DiT loaders), ONNX Runtime Mobile (general C++/FFI, high transpose-op overhead), and Google LiteRT (native PyTorch conversion, direct NPU bindings, zero-copy buffers).

---

### Chapter 3: System Architecture and Algorithmic Formulation
**Source File:** [Chapters/Chapter3.tex](file:///c:/voice_cloning/midsem_report/Chapters/Chapter3.tex) (Lines 1 to 311)

* **Section 3.1: Architectural Progression from Proof of Concept to Production Pipeline**:
  * *Phase 1 (Mobile Feasibility PoC)*: ZipVoice-Distill 123M Zipformer + 4-step flow matching + INT8 Vocos (104 MB model) via Sherpa-ONNX in Flutter.
  * *Empirical PoC Findings & Inferences*: Bounded CPU execution verified, but discovered the 1.5 GB memory cliff on 4 GB school hardware, the Fixed Overhead Anomaly, and the fundamental linguistic inadequacy of existing off-the-shelf mobile models for Indic curricula.
  * *Phase 2 (Primary Indic Production Engine)*: IndicF5 335M 22-layer DiT + 8-step Euler ODE solver with Classifier-Free Guidance ($\gamma = 2.0$) and Sway Scheduling ($\rho = -1.0$) + INT8 Vocos (349 MB DiT + 22 MB vocoder, 801 MB peak RSS).
  * *Phase 3 (Strategic Edge Acceleration)*: Migration to Google LiteRT for Qualcomm QNN HTP and MediaTek NeuroPilot NPU offloading alongside 2-step FlashSpeech distillation.
* **Section 3.2: Signal Preprocessing and Acoustic Feature Extraction**:
  FFmpeg ingestion to 24 kHz mono 16-bit PCM WAV. Root-Mean-Square (RMS) amplitude normalization scaled to target $\text{RMS} = 0.10$ with clamping $[-1.0, 1.0]$. 100-channel log-mel filterbank extraction with $N_{\text{fft}} = 1024$, hop size $H = 256$, Hanning window.
* **Section 3.3: Indic Akshara Dynamics and Syllabic Duration Modeling**:
  * *Duration Mismatch Problem*: Naive heuristic ($15.0 \times \text{len}(\mathbf{w})$) over-allocated duration by 2.5x, forcing the DiT to integrate beyond text conditioning, synthesizing breathing, whispering, and repeated babble artifacts.
  * *Calibrated Formula*: Derived from IndicVoices phonetic distribution:
    $$\tau_{\text{char}} \approx 54\text{--}60\text{ ms} \implies k_{\text{mel}} = 6.5\text{ mel frames per Unicode character}$$
    $$T_{\text{gen}} = \left\lfloor \frac{N_{\text{chars}} \times 6.5}{\text{speed}} \right\rfloor + \tau_{\text{pad}} \quad (\tau_{\text{pad}} = 28\text{ frames} \approx 0.30\text{ s})$$
* **Section 3.4: Formal Algorithmic Formulations**:
  * **Algorithm 1**: *On-Device Indic Zero-Shot Continuous Flow-Matching Synthesis* (complete pseudocode including audio concat, Euler loop, sway time steps, CFG velocity update, target mel slicing, and Vocos invocation).
  * **Algorithm 2**: *Vocos Neural Fourier Audio Synthesis* (ConvNeXt backbone, linear magnitude head, linear phase cosine/sine heads, complex spectrogram assembly $\mathbf{Z} \in \mathbb{C}^{513 \times T}$, and inverse STFT).
* **Section 3.5: Comparative Model Architectural Matrix**:
  Full comparison table evaluating IndicF5 (Primary Production), ZipVoice (Mobile Feasibility PoC), GPT-SoVITS, Chatterbox, XTTS-v2, Kokoro-82M, and VITS across parameter counts, paradigm, quantization, zero-shot capacity, Indic support, and edge feasibility.

---

### Chapter 4: Implementation Methodology and Engineering Iterations
**Source File:** [Chapters/Chapter4.tex](file:///c:/voice_cloning/midsem_report/Chapters/Chapter4.tex) (Lines 1 to 272)

Chronicles the 10 engineering milestones executed during the project:
1. **Iteration 1: Mobile Feasibility Proof of Concept (ZipVoice-Distill via Sherpa-ONNX)**: Validated 4-step non-autoregressive flow matching on CPU ($\text{RTF} \approx 0.35$), confirming low-step viability without multi-minute diffusion delays.
2. **Iteration 2: Flutter Mobile PoC Prototype (`voice_clone_proto`)**: Built 4-step wizard UI for teachers to record reference audio and generate classroom lesson aids. Decoupled inference into background Dart Isolate (`Isolate.run()`). Integrated TalkBack accessibility semantics for blind learners.
3. **Iteration 3: Multi-Device Benchmarking of the PoC and Empirical Inferences**: Tested across 4 silicon tiers (Snapdragon 8 Gen 2, Exynos 1380, Dimensity 900, Lenovo Tab K10). Implemented live in-kernel `/proc/self/status` profiling hook. Formulated the 4 foundational inferences: (1) mandatory static INT8 quantization to avoid the 1.5 GB LMK ceiling on school hardware; (2) warm in-memory pipelines to overcome the Fixed Overhead Anomaly; (3) linguistic inadequacy of off-the-shelf mobile models for Indic curricula; and (4) NPU offloading necessity via Google LiteRT.
4. **Iteration 4: Transition to IndicF5: Multilingual Adaptation and Desktop Verification**: Ported AI4Bharat PyTorch weights (1.35 GB `model.safetensors`). Built standalone `clone.py` verifying zero-shot synthesis across Tamil, Telugu, Kannada, and Devanagari Hindi.
5. **Iteration 5: Syllabic Duration Calibration**: Fixed trailing silence and audio truncation by enforcing $k_{\text{mel}} = 6.5$ mel frames/char with 0.30s post-utterance acoustic buffer.
6. **Iteration 6: Reference Audio Duration Boundary Law**: Discovered ConvNeXt spatial alignment collapse when reference audio exceeds 5.0s ($T_{\text{ref}} > 500$ frames). Established operational law: $3.5 \le \Delta t_{\text{ref}} \le 5.0$ seconds.
7. **Iteration 7: In-Memory Warm Model Batch Synthesis & Dataset**: Built `batch.py` with warm RAM model caching. Curated `prompts.json` (120 phrases across Tamil, Telugu, Hindi stratified across Short, Medium, Midlong, Long tiers).
8. **Iteration 8: Unified Voice Studio Suite & Catalog Management**: Refactored Python package into modular architecture (`src/voice_studio/`) with interactive TUI and voice catalog (`samples/voices.json`) supporting teacher profiles for different school subjects.
9. **Iteration 9: Graph Optimization & Static INT8 Quantization**: Exported FP32 static/dynamic ONNX graphs and static INT8 quantized models. DiT compressed from 1.35 GB to 349 MB (74% reduction); Vocos vocoder compressed from 54 MB to 22 MB.
10. **Iteration 10: Custom Native C++ Engine & Dart FFI**: Built `libindicf5_engine.so` linking to ONNX Runtime Mobile C++ API with pre-allocated static memory arenas and ARM NEON SIMD kernels. Created Dart FFI bridge service (`indicf5_service.dart`).
* **Section 4.11: Hardware Memory Budget Analysis on 4 GB Platforms**:
  Table proving total peak RSS is bounded to **801 MB** (349 MB DiT + 22 MB Vocos + 280 MB static arenas + 150 MB Flutter/UI), leaving a **+699 MB safety headroom** below the Android LMK 1,500 MB ceiling.

---

### Chapter 5: Strategic Future Architecture: Google LiteRT & Edge Acceleration Roadmap
**Source File:** [Chapters/Chapter5.tex](file:///c:/voice_cloning/midsem_report/Chapters/Chapter5.tex) (Lines 1 to 176)

* **Section 5.1: Motivation for Transitioning to Google LiteRT**:
  Addresses the three bottlenecks of custom ONNX Runtime Mobile: transpose-op layout degradation, heterogeneous accelerator driver fragmentation, and user-space memory copy penalties.
* **Section 5.2: Direct PyTorch Conversion via LiteRT Torch (`litert-torch`)**:
  PyTorch 2.x `torch.export` export flow directly into `.tflite` FlatBuffers. StableHLO dialect operator fusion (fusing QKV linear projections, rotary embeddings, and layer norm).
* **Section 5.3: Hardware Acceleration via CompiledModel API**:
  Unified declarative accelerator priority (`NPU` $\to$ `GPU` $\to$ `CPU`). Qualcomm AI Engine Direct (QNN HTP) offloading for Snapdragon, MediaTek NeuroPilot for Dimensity/Helio, and XNNPACK 4-thread ARM NEON fallback for budget CPUs.
* **Section 5.4: Zero-Copy Pipelines via Android Hardware Buffers**:
  Utilizes `AHardwareBuffer` memory mapping between DiT mel output, Vocos vocoder input, and AAudio/OpenSL ES output tracks to eliminate user-space memory copies.
* **Section 5.5: Trajectory Distillation (2-Step and 4-Step Sampling)**:
  * 4-Step Reflow: 2-rectified flow straightening eliminating trajectory intersections.
  * 2-Step Consistency Distillation (FlashSpeech): Step 1 generates harmonic formant structure; Step 2 synthesizes high-frequency fricatives and fine phonetics.
* **Section 5.6: Physical Testing and Verification Protocol**:
  Structured 3-phase protocol: (Phase A) Graph Parity (MCD $< 3.5$ dB), (Phase B) Ahead-of-Time NPU Compilation (100% layer delegation), (Phase C) Sustained Load Profiling on Lenovo Tab K10 ($\text{RSS} < 850$ MB).

---

### Chapter 6: Conclusion, Societal Impact and Research Summary
**Source File:** [Chapters/Chapter6.tex](file:///c:/voice_cloning/midsem_report/Chapters/Chapter6.tex) (Lines 1 to 60)

* **Section 6.1: Summary of Research Accomplishments**:
  Recapitulates the 8 primary milestones achieved during the mid-semester phase.
* **Section 6.2: Key Scientific, Systems, and Societal Contributions**:
  * *Theoretical/Linguistic*: Akshara mel frame density characterization and cross-lingual zero-shot inpainting without phonetic dictionaries.
  * *Systems/Edge*: In-kernel memory profiling, Fixed Overhead Anomaly characterization, static INT8 quantization, and 801 MB memory confinement.
  * *Pedagogical/Accessibility*: Familiar-voice learning for government school children, accessible auditory study for visually impaired students, and zero-cost offline deployment protecting teacher biometric privacy.
* **Section 6.3: Concluding Remarks and Immediate Priorities**:
  Prioritizes the 5 post-midsem execution goals: (1) Google LiteRT migration, (2) NPU hardware delegation, (3) 2-step consistency distillation, (4) Lenovo Tab K10 sustained load profiling, and (5) Classroom accessibility and Flutter UI integration for pilot trials.

---

### Appendices

* **[Appendix A: Mathematical Derivations and Numerical Proofs](file:///c:/voice_cloning/midsem_report/Appendices/AppendixA.tex)**:
  * *Section A.1*: Derivation of the Optimal Transport Flow Matching Objective. Proves gradient equivalence between marginal loss $\mathcal{L}_{\text{Marginal}}(\theta)$ and conditional loss $\mathcal{L}_{\text{CFM}}(\theta)$.
  * *Section A.2*: Sway Sampling Schedule Formulation. Derives the non-uniform time transformation $s(t) = t + \rho \cdot t(1 - t)(1 - 2t)$ for $\rho = -1.0$, which concentrates Euler integration steps near boundaries $t=0$ and $t=1$.
* **[Appendix B: Multilingual Phonetic Evaluation Prompts Dataset](file:///c:/voice_cloning/midsem_report/Appendices/AppendixB.tex)**:
  * *Section B.1*: Dataset architecture and stratification methodology (Short, Medium, Midlong, Long tiers).
  * *Section B.2*: Telugu Dataset Inventory (native Telugu script and English translations, e.g., నువ్వు భోజనం చేశావా?).
  * *Section B.3*: Tamil Dataset Inventory (native Tamil script and English translations, e.g., வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?).
  * *Section B.4*: Hindi Dataset Inventory (native Devanagari script and English translations, e.g., नमस्ते, आप कैसे हैं?).

---

## Technical Specifications Cheat-Sheet

| Parameter | Value | Technical Context |
|---|---|---|
| **Acoustic Sampling Rate** ($f_s$) | 24,000 Hz | Standard for high-fidelity speech synthesis |
| **STFT Window / Hop Size** | $N_{\text{fft}} = 1024, H = 256$ | Frame duration $\Delta t_{\text{frame}} = 10.667$ ms |
| **Mel Spectrogram Channels** | 100 channels | Log-compressed filterbank |
| **RMS Target Level** | 0.10 (clamped $[-1.0, 1.0]$) | Reference gain standardization |
| **Akshara Duration Constant** ($k_{\text{mel}}$) | 6.5 mel frames / char | $\tau_{\text{char}} \approx 54\text{--}60$ ms per character |
| **Post-Utterance Acoustic Buffer** | 28 frames ($\approx 0.30$ s) | Prevents trailing audio truncation |
| **Reference Clip Boundaries** | $3.5 \le \Delta t_{\text{ref}} \le 5.0$ s | Prevents ConvNeXt attention window collapse |
| **ODE Numerical Solver** | 8-step Euler | Sway $\rho = -1.0$, CFG $\gamma = 2.0$ |
| **Unquantized FP32 Footprint** | 1.35 GB weights | Peak RSS: 2,404 MB (Triggers Android LMK crash) |
| **Quantized INT8 Footprint** | 349 MB DiT + 22 MB Vocos | Peak RSS: 801 MB (+699 MB safe headroom) |
| **Android LMK Process Limit** | $\approx 1,500$ to $1,800$ MB RSS | Strict physical RAM limit on 4 GB devices |
