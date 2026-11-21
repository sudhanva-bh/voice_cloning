# CONSISTENCY CHECK: Global Numerical and Conceptual Audit

**Project Title:** On-Device Indic Voice Cloning and Text-to-Speech Synthesis for Edge Architectures  
**Course:** CS F377 Design Project  
**Author:** Sudhanva B H  
**Audit Date:** October 13, 2026  

This document records the results of the global consistency audit conducted across the entire mid-semester report LaTeX source files (`main.tex`, `Chapters/Chapter1.tex` through `Chapter6.tex`, and `Appendices/AppendixA.tex` through `AppendixB.tex`). It confirms that all conceptual distinctions, numerical parameters, and experimental findings are internally consistent, mathematically sound, and rigorously differentiated throughout the text.

---

## 1. Audit of Core Conceptual Distinctions

| Conceptual Dimension | Distinction Enforced Across All Chapters | Verification Status |
|---|---|---|
| **ZipVoice vs. IndicF5** | **ZipVoice-Distill** is strictly identified as the *implemented and benchmarked mobile Proof of Concept (PoC)* (using Sherpa-ONNX in Flutter) to evaluate edge feasibility.<br>**IndicF5** is strictly identified as the *primary multilingual Indic production engine* (335M Diffusion Transformer + custom C++ engine + INT8 quantization + Vocos). The two systems are never conflated as dual engines. | **PASS** — Consistently separated in Abstract, Chapters 1, 3, 4, 5, 6, and Figures 3.1 & 4.3. |
| **Physical Measurements vs. Analytical Estimates** | **Physical Measurements:** Direct in-kernel readings (`/proc/self/status`) obtained from actual hardware execution of ZipVoice on the Lenovo Tab K10 (8.97× to 19.99× RTF; 1,276 to 2,491 MB `VmRSS`).<br>**Analytical Estimates:** The 801 MB figure is strictly labeled as a *theoretical component-level memory budget* for the quantized IndicF5 pipeline (349 MB DiT + 22 MB Vocos + 280 MB arenas + 150 MB runtime), not measured RSS. | **PASS** — Claims that IndicF5 was physically confirmed at 801 MB on the K10 have been completely eliminated. |
| **Post-Utterance VmRSS vs. Peak RSS** | Measurements on the Lenovo Tab K10 are explicitly labeled as **post-utterance resident memory (`VmRSS`)** sampled immediately after utterance completion. They are never described as continuous peak RSS, and the observed allocation variability is analyzed. Earlier device readings retain their historical label as peak RSS. | **PASS** — Distinct column headings in Table 4.1, Table 4.2, and Section 4.4.2. |
| **Means vs. Medians** | **Lenovo Tab K10:** Reported statistics are the **arithmetic means** of three independent trials per tier (Short: 18.222×, Med: 10.783×, Long: 11.197×).<br>**Flagship/Mid-Range Devices:** Retain their previously reported **median** values (N=1 trial tier). | **PASS** — Explicitly labeled in Table 4.1 and Table 4.2. Medians were not relabeled as means. |
| **Implemented vs. Proposed Architectures** | **Implemented & Operational:** ZipVoice Flutter Android app; desktop IndicF5 PyTorch cloning; calibrated duration model; FP32/INT8 ONNX model export; custom C++ native engine (`libindicf5_engine.so`) with static arenas; Prompts dataset.<br>**Proposed & Future Work:** Sampling step distillation (FlashSpeech 2-step); Google LiteRT FlatBuffer conversion; hardware delegate offloading (Qualcomm QNN HTP, MediaTek NeuroPilot). | **PASS** — Formally distinguished in Section 3.1, Figure 3.1, Figure 4.3, Figure 5.1, and Section 6.4. |
| **Hardware Capabilities (Lenovo Tab K10 vs. NPU)** | The Lenovo Tab K10's MediaTek Helio P22T is explicitly identified as an entry-level processor **lacking any NPU or deep learning accelerator**. The report clarifies that Qualcomm QNN and MediaTek NeuroPilot *cannot* accelerate the K10, and focuses K10 optimizations purely on CPU-side ARM NEON execution, static arenas, and step distillation. | **PASS** — Decoupled in Section 4.4.3, Section 5.3, Section 6.1, and Figure 5.1. |

---

## 2. Global Numerical Audit Table

| Parameter / Metric | Corrected Value in Report | Prior Inconsistency / Defect | Where Verified in Source Code |
|---|---|---|---|
| **Tab K10 Short RTF** | **18.222× (Mean)**<br>(Trials: 17.860×, 16.820×, 19.986×) | Previously listed as an unverified estimate "$>5.0$" | Table 4.1, Table 4.2, §4.4.2, §4.4.3, Fig. 4.1 |
| **Tab K10 Medium RTF** | **10.783× (Mean)**<br>(Trials: 10.467×, 11.688×, 10.194×) | Previously absent | Table 4.1, Table 4.2, §4.4.2, §4.4.3, Fig. 4.1 |
| **Tab K10 Long RTF** | **11.197× (Mean)**<br>(Trials: 15.049×, 9.573×, 8.968×) | Previously absent | Table 4.1, Table 4.2, §4.4.2, §4.4.3, Fig. 4.1 |
| **Tab K10 Short VmRSS** | **1,291.7 MB (Mean Post-VmRSS)**<br>(Range: 1,276–1,301 MB) | Previously conflated with IndicF5 801 MB | Table 4.1, Table 4.2, §4.4.2, §4.4.3, Fig. 4.2 |
| **Tab K10 Medium VmRSS** | **1,923.3 MB (Mean Post-VmRSS)**<br>(Range: 1,532–2,337 MB) | Previously absent; showed substantial variance | Table 4.1, Table 4.2, §4.4.2, §4.4.3, Fig. 4.2 |
| **Tab K10 Long VmRSS** | **2,394.7 MB (Mean Post-VmRSS)**<br>(Range: 2,326–2,491 MB) | Peak reached 2,491 MB without LMK termination | Table 4.1, Table 4.2, §4.4.2, §4.4.3, Fig. 4.2 |
| **LMK Terminations on K10** | **0 / 9 Terminations** | Prior text asserted >1,500 MB causes an inevitable crash | Table 4.2, §4.4.3, §6.1, Abstract |
| **IndicF5 Analytical Budget** | **801 MB**<br>(349 MB DiT + 22 MB Vocos + 280 MB arenas + 150 MB runtime) | Previously described as measured physical RSS on K10 | Abstract, §3.1, §4.12, Table 4.3, §6.1, §6.2 |
| **Working Arena Memory** | **280 MB Static** vs. **850 MB Dynamic** (up to 1,200 MB for long sequences) | Reconciled the 850 MB vs. 1.2 GB activation claims | Table 4.3, §4.12 |
| **Syllabic Duration Constant** | **6.5 mel frames per character** = **69.33 ms** per code point | Previously cited as 55 ms ($55\text{ ms} = 5.16\text{ frames}$; arithmetic inconsistency) | Abstract, §2.8.2, §3.3, §4.6.3, §6.1 |
| **Akshara Syllable Duration** | **111 to 153 ms** per akshara<br>(1.6 to 2.2 Unicode code points) | Correctly distinguishes Unicode characters from spoken Indic syllables | §2.8.2, §3.3, §4.6.3, §6.1 |
| **Sway Sampling Formula** | $t_i = 1 - \cos\left(\frac{\pi}{2}s_i\right)$ (for $\rho = -1.0$) | Matched exact F5-TTS implementation (`f5_tts/model/cfm.py`) | §2.7, §3.6, Algorithm 1 |
| **Reference Audio Window** | **3.5 to 5.0 seconds** ($\approx 328$ to 468 mel frames) | Framed as an empirical operating rule avoiding attention dispersion | §4.7.3, §6.1 |
| **IndicF5 DiT INT8 Model Size** | **~349 MB** (down from 1.35 GB FP32, 74% reduction) | Matches physical file `indicf5_dit_int8_static.onnx` (349,055,195 B) | Abstract, §3.1, §4.10, Table 4.3, §6.1 |
| **Vocos INT8 Model Size** | **~22 MB** (down from 54 MB FP32) | Matches physical file `indicf5_vocos_int8.onnx` (22,119,090 B) | Abstract, §2.5, §3.1, §4.10, Table 4.3, §6.1 |
| **ZipVoice PoC Asset Sizes** | **5.5 MB Encoder**, **124.7 MB Decoder**, **54 MB Vocos** | Matches physical files in `voice_clone_proto/assets/zipvoice` | §4.2.2 |
| **Evaluated Languages** | **4 Languages** tested for cloning (Tamil, Telugu, Kannada, Hindi); **3 Languages** in `prompts.json` (Tamil, Telugu, Hindi; 120 phrases) | Reconciled language counts across text and appendix | §4.5.3, §4.8.3, Appendix B |
| **List of Figures** | **6 Figures total** (3.1, 3.2, 4.1, 4.2, 4.3, 5.1), all resolved with full captions | Previously empty List of Figures | Page viii of `main.pdf` |

---

## 3. Verification Conclusion

Every metric, formula, and conceptual boundary has been verified through automated cross-referencing and successfully compiled with Tectonic into the final submission-ready document `main.pdf`. The report is technically robust, internally consistent, and thoroughly defensible for academic faculty evaluation.
