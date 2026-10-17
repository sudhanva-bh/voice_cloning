# CHANGELOG: Technical and Editorial Revision of CS F377 Mid-Semester Report

**Project Title:** On-Device Indic Voice Cloning and Text-to-Speech Synthesis for Edge Architectures  
**Institution:** BITS Pilani, Hyderabad Campus  
**Course:** CS F377 Design Project  
**Author:** Sudhanva B H  
**Revision Date:** October 13, 2026  

This document details all technical, mathematical, architectural, and editorial modifications executed across the LaTeX source files of the mid-semester report, ensuring strict internal consistency, empirical precision, and academic rigor.

---

## 1. `main.tex`

| Section / Element | Modification Made | Technical Rationale |
|---|---|---|
| **Abstract (Page 2)** | Completely restructured abstract into four structured paragraphs; integrated measured Lenovo Tab K10 ZipVoice benchmarks (8.97× to 19.99× RTF, post-utterance `VmRSS` 1,276–2,491 MB, 0 LMK terminations); labeled 801 MB as an analytical component budget for IndicF5; updated duration constant to 6.5 mel frames (~69.3 ms/character); preserved layout strictly within Roman page `i` (Page 2) without spilling to Page 3. | Replaces unverified claims of "801 MB experimentally confirmed on Lenovo" and an "invariant 1,500 MB crash ceiling"; accurately communicates the separate roles of the ZipVoice PoC and IndicF5 production engine. |
| **Acknowledgements (Page 3)** | Corrected grammatical phrasing: "extend my gratitude", "in the AI domain", and "as part of the Design Project". | Polish and professional academic tone. |
| **Preamble & Packages** | Added `\usepackage{array}`, `\usepackage{float}`, and font definitions for Indic scripts (`\indicfont`, `\telugufont`, `\tamilfont`); ensured graphics paths include `Figures/`. | Supported verified rendering of native Indian scripts and custom vector graphics. |

---

## 2. `Chapters/Chapter1.tex` (Introduction & Background)

| Section / Element | Modification Made | Technical Rationale |
|---|---|---|
| **§1.1 Context & Motivation** | Framed pedagogical benefits (familiar-teacher voice engagement, auditory learning for visually impaired students) as targeted educational goals rather than experimentally proven psychological outcomes. | Distinguishes technical contributions from unconducted behavioral user studies. |
| **§1.3 Ethics & Biometric Privacy** | Replaced claims of "absolute biometric privacy" with precise statements that offline on-device inference creates a verifiable privacy boundary by avoiding data transmission to cloud APIs; added discussion of local teacher consent and deletion. | Scientifically defensible framing of data security and biometric ethics. |
| **§1.4.3 F5-TTS Architecture** | Replaced incorrect descriptions of "cross-attention" with fused sequence conditioning and bidirectional self-attention with Rotary Position Embeddings (RoPE). | Accurately describes the actual F5-TTS architecture where ConvNeXt-V2 text embeddings, noisy mel, and acoustic prefix are concatenated along feature channels. |
| **§1.5 Android Memory Management** | Revised description of Android low-memory management to account for modern userspace `lmkd`, pressure stalls (`/proc/pressure/memory`), and ZRAM swap compression; removed claims that Android completely disables swap and that 1,500 MB is a universal hard kill threshold. | Aligns systems theory with modern Linux/Android kernel realities and our experimental findings. |
| **§1.6.5 Latency & RTF Breakdown** | Replaced assertion of an invariant "1.2-second cold-start initialization penalty" with an explanation of unamortized setup costs and stage-level latency components. | Avoids asserting speculative stage latency numbers without per-stage profiling data. |
| **Acronym Handling** | Fixed duplicated acronym expansions (e.g., `Text-to-Speech (Text-to-Speech (TTS))` -> `\gls{tts}`). | Eliminates LaTeX macro expansion defects. |

---

## 3. `Chapters/Chapter2.tex` (Theoretical Foundations & Literature Survey)

| Section / Element | Modification Made | Technical Rationale |
|---|---|---|
| **§2.2 VITS & Flow Architectures** | Corrected description of VITS from continuous normalizing flows to finite normalizing flows (stacked affine coupling layers with invertible $1 \times 1$ convolutions). | Architectural accuracy based on primary literature (Kim et al., 2021). |
| **§2.3 Flow Matching Mathematics** | Clarified the distinction between straight conditional paths and curved marginal velocity fields; explained that conditional straight paths do not guarantee trivial few-step ODE integration without trajectory straightening. | Mathematical precision regarding Lipman et al. (2022) flow matching theory. |
| **§2.4 DiT & Conditioning** | Clarified that F5-TTS concatenates noised mel, audio prefix, and ConvNeXt-V2 text representations along the feature channel dimension ($[\mathbf{x}_t \,\|\, \mathbf{x}_{\text{cond}} \,\|\, \mathbf{e}_{\text{text}}]$), feeding all 22 bidirectional self-attention DiT layers. | Eliminates lingering claims of cross-attention mechanisms. |
| **§2.5 Neural Vocoding (Vocos)** | Added explanation of complex STFT Hermitian symmetry ($N_{\text{fft}}/2 + 1 = 513$ frequency bins at $N_{\text{fft}} = 1024$); identified Vocos INT8 weight size as ~22 MB compared to 54 MB FP32. | Resolves physical file size and mathematical signal processing definitions. |
| **§2.7 Sway Sampling** | Updated sway schedule formula to match the exact F5-TTS codebase: $t(s) = s + c(\cos(\frac{\pi}{2}s) - 1 + s)$, which simplifies to $t(s) = 1 - \cos(\frac{\pi}{2}s)$ when $c = -1.0$. | Reconciles mathematical derivation with `f5_tts/model/cfm.py`. |
| **§2.8 Indic Phonetics & Duration** | Corrected duration arithmetic: at 24 kHz and hop size 256, 1 mel frame = 10.667 ms. $6.5 \text{ frames} = 69.33\text{ ms}$ per Unicode code point. Connected this to Indic aksharas (1.6–2.2 code points $\to$ 111–153 ms per spoken syllable). | Fixes arithmetic error where 6.5 frames was mistakenly cited as 55 ms. |

---

## 4. `Chapters/Chapter3.tex` (Proposed System Architecture)

| Section / Element | Modification Made | Technical Rationale |
|---|---|---|
| **§3.1 Architectural Overview** | Formally partitioned the system into three distinct phases: (1) Implemented & benchmarked ZipVoice PoC, (2) Primary IndicF5 production pipeline (DiT + INT8 Vocos + C++/Dart FFI), and (3) Strategic LiteRT acceleration roadmap. | Enforces strict distinction between operational PoC and developing Indic engine. |
| **Figure 3.1** | Inserted `Figures/system_architecture.pdf` (vector PDF) with full caption and label `\label{fig:system_architecture}`. | Provides clear visual separation of project phases in the List of Figures. |
| **§3.3 Duration Formulation** | Updated Equations 3.10–3.12: $\tau_{\text{char}} = 6.5 \times \frac{256}{24000}\text{ s} \approx 69.33\text{ ms}$; clarified that character counts serve as an empirical proxy for akshara syllables. | Resolves mathematical contradiction with frame rate constants. |
| **Figure 3.2** | Inserted `Figures/indicf5_pipeline.pdf` (vector PDF) illustrating the zero-shot inference pipeline with fused conditioning and 8-step Euler ODE solver. | Replaces missing figures with an accurate architectural diagram. |
| **§3.6 & Algorithm 1** | Updated Classifier-Free Guidance update and sway time step calculation to $t_i = 1 - \cos(\frac{\pi}{2}s_i)$. | Aligns pseudocode with verified implementation. |

---

## 5. `Chapters/Chapter4.tex` (Implementation Methodology & Iterations)

| Section / Element | Modification Made | Technical Rationale |
|---|---|---|
| **Table 4.1** | Replaced estimated K10 entry with confirmed experimental arithmetic means: Short (18.222× RTF, 1,291.7 MB VmRSS), Medium (10.783× RTF, 1,923.3 MB VmRSS), Long (11.197× RTF, 2,394.7 MB VmRSS), PASS (N=3). Maintained distinct labels for earlier devices (Medians, Peak RSS). | Accurately integrates real-device experimental findings. |
| **Table 4.2** | Added complete raw experimental dataset table containing all 9 individual trial observations for ZipVoice on the Lenovo Tab K10. Wrapped in `\resizebox` to prevent margin overflow. | Full experimental transparency and reproducibility. |
| **Figures 4.1 & 4.2** | Inserted `Figures/lenovo_rtf.pdf` (mean RTF by tier with trial bounds) and `Figures/lenovo_vmrss.pdf` (post-utterance resident memory across all 9 trials). | Fulfills Task 4 plotting requirements without arbitrary LMK ceiling lines. |
| **§4.4.3 Empirical Inferences** | Extensively rewritten: explained that ZipVoice completed all 9 trials without LMK termination; resident memory ranged up to 2,491 MB, directly refuting the 1,500 MB crash ceiling; analyzed allocation variability (1,532 MB vs 2,337 MB in medium tier); noted that CPU execution is operational but slower than real time. | Derives defensible engineering conclusions from physical data. |
| **Iteration 5 (Duration)** | Updated text to reflect $6.5 \text{ frames} = 69.33\text{ ms}$ per Unicode code point (~111–153 ms per akshara). | Internal consistency with Chapters 2 and 3. |
| **Iteration 6 (Long Reference)** | Corrected explanation of long-reference degradation to reflect fused conditioning channel zero-padding and attention dispersion under bidirectional self-attention with RoPE. | Replaces cross-attention inaccuracies. |
| **Iteration 9 (Model Artifacts)** | Reconciled listed artifacts: 1 PyTorch checkpoint, 4 ONNX graphs, and 1 vocab mapping (6 total items); clarified that `indicf5_dit_int8_static.onnx` features both static calibration and fixed 128-frame dimensions for memory arena benchmarking, whereas dynamic sequences require dynamic axis handling. | Resolves Task 2.5 and 2.6 discrepancies. |
| **Figure 4.3** | Inserted `Figures/runtime_architecture.pdf` illustrating Flutter UI, Dart isolate, Dart FFI, C++ engine, and ONNX Runtime session. | Visualizes the developed deployment architecture. |
| **§4.12 & Table 4.3** | Renamed table to "Analytical Memory Budget for the Proposed Quantized IndicF5 Deployment"; explicitly labeled 801 MB as a theoretical component sum (349 MB DiT + 22 MB Vocos + 280 MB arenas + 150 MB runtime); clarified that dynamic activation memory in unquantized FP32 reaches up to 1,200 MB for long sequences. | Replaces claims that IndicF5 was physically measured at 801 MB on the K10. |
| **§4.13 (Evaluation Limitations)** | Added dedicated section detailing post-midsem validation plans: objective voice quality (WER/CER/MOS), speaker embedding cosine similarity, INT8 acoustic degradation studies, and quantized IndicF5 on-device profiling. | Fulfills Task 6.1 by presenting evaluation gaps naturally as future work. |

---

## 6. `Chapters/Chapter5.tex` (Future Roadmap: Google LiteRT)

| Section / Element | Modification Made | Technical Rationale |
|---|---|---|
| **Figure 5.1** | Inserted `Figures/optimization_roadmap.pdf` contrasting CPU-only execution with operator fusion, step distillation, and hardware delegates. | Fulfills Task 4 roadmap visualization. |
| **§5.3 Hardware Delegation** | Decoupled Lenovo Tab K10 from NPU delegation; explicitly clarified that the MediaTek Helio P22T lacks dedicated NPU silicon and cannot be accelerated by Qualcomm QNN or MediaTek NeuroPilot; focused K10 optimizations on CPU-side ARM NEON execution, arena reuse, and step distillation. | Prevents scientifically indefensible claims of NPU execution on the K10. |
| **§5.3.2 Throughput Projections** | Qualified sub-0.5× RTF projections on flagship Snapdragon platforms as analytical engineering targets rather than verified results. | Eliminates unvalidated performance promises. |
| **§5.6 Phase C Protocol** | Rephrased resident memory profiling on the K10 to evaluate progress toward the 850 MB design target, removing claims of an unconditional guarantee. | Scientifically sound verification framing. |

---

## 7. `Chapters/Chapter6.tex` (Conclusion & Summary)

| Section / Element | Modification Made | Technical Rationale |
|---|---|---|
| **§6.1 Milestone Summary** | Updated summary points to reflect real Lenovo measurements (8.97×–19.99× RTF, up to 2,491 MB VmRSS, 0 LMK terminations); labeled 801 MB as an analytical budget; corrected duration constant to 6.5 frames / 69.33 ms; qualified educational impact. | Ensures conclusion precisely mirrors the revised body of the report. |
| **§6.2 Contributions** | Replaced claims of "safely bounded within 801 MB physical memory" with the formulation of an analytical component budget and empirical demonstration of mobile flow-matching execution. | Eliminates factual overstatements. |
| **§6.3 Ethics & Privacy** | Added complete subsection on teacher consent, local storage, verifiable deletion, voice impersonation mitigation, cryptographic security, and offline biometric privacy boundaries. | Fulfills Task 6.3 ethical governance requirements. |
| **§6.4 Immediate Priorities** | Ordered post-midsem priorities realistically: LiteRT migration, CPU and accelerator optimization, sampling step distillation (Reflow & FlashSpeech), on-device IndicF5 profiling, and perceptual evaluation. | Defensible engineering roadmap. |

---

## 8. Summary of Figures and Visual Assets

All visual figures were generated as publication-quality vector PDFs and added to `Figures/`:
1. `Figures/system_architecture.pdf` (and `system_architecture.mmd`): End-to-end multi-phase architecture.
2. `Figures/indicf5_pipeline.pdf` (and `indicf5_pipeline.mmd`): Zero-shot IndicF5 conditioning and ODE sampling pipeline.
3. `Figures/runtime_architecture.pdf` (and `runtime_architecture.mmd`): Native C++/Dart FFI/ONNX Runtime architecture.
4. `Figures/optimization_roadmap.pdf` (and `optimization_roadmap.mmd`): Optimization roadmap.
5. `Figures/lenovo_rtf.pdf`: Mean RTF by utterance tier with exact trial bounds on Lenovo Tab K10.
6. `Figures/lenovo_vmrss.pdf`: Post-utterance resident memory across all 9 Lenovo trials.
7. `Figures/generate_figures.py`: Fully reproducible Python script generating all six figures.
