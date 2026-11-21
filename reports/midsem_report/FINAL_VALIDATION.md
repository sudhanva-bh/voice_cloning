# FINAL VALIDATION REPORT — CS F377 PROJECT REPORT

**Project:** On-Device Indic Voice Cloning and Text-to-Speech Synthesis for Edge Architectures  
**Course:** CS F377 Design Project, BITS Pilani, Hyderabad Campus  
**Date:** October 13, 2026  
**Document:** Mid-Semester Project Report (`main.pdf`, 75 pages)

---

## 1. Confirmation of Critical Technical Invariants

### 1.1 Lenovo Tab K10 Empirical Data Integrity
- **Status:** **CONFIRMED & UNCHANGED**
- All nine experimental trials on the Lenovo Tab K10 (MediaTek Helio P22T, 4 GB RAM) recorded in Table 4.2 remain verbatim:
  - **Short Tier (~5 words):** Trial 1: $17.860\times$ (1,301 MB); Trial 2: $16.820\times$ (1,298 MB); Trial 3: $19.986\times$ (1,276 MB). **Mean:** $18.222\times$ RTF, $1,291.7$ MB post-utterance `VmRSS`.
  - **Medium Tier (~25 words):** Trial 1: $10.467\times$ (2,337 MB); Trial 2: $11.688\times$ (1,532 MB); Trial 3: $10.194\times$ (1,901 MB). **Mean:** $10.783\times$ RTF, $1,923.3$ MB post-utterance `VmRSS`.
  - **Long Tier (~65 words):** Trial 1: $15.049\times$ (2,326 MB); Trial 2: $9.573\times$ (2,491 MB); Trial 3: $8.968\times$ (2,367 MB). **Mean:** $11.197\times$ RTF, $2,394.7$ MB post-utterance `VmRSS`.
- **Termination Record:** Exactly **0 LowMemoryKiller terminations in 9 trials**.
- **Sampling Procedure:** Memory is explicitly documented as **post-utterance `VmRSS`** sampled from `/proc/self/status` upon completion of inference, not continuous peak RSS.
- **Statistical Description:** Category metrics are explicitly identified as **arithmetic means**, and error bars in Figure 4.1 are clearly labeled as **observed minimum and maximum trial ranges**, not parametric confidence intervals.

---

### 1.2 Separation Between ZipVoice PoC and IndicF5 Pipeline
- **Status:** **CONFIRMED & STRICTLY SEPARATED**
- The document formally maintains the distinction between the three architectural tiers:
  1. **Phase 1 (Implemented & Benchmarked):** ZipVoice-Distill PoC (123M parameters, Sherpa-ONNX runtime, Flutter Android app). All physical mobile benchmarks (Lenovo Tab K10, Samsung S23, Tab S9 FE+, M53) are strictly attributed to this PoC.
  2. **Phase 2 (Implemented Engineering Pipeline):** IndicF5 multilingual architecture (335M parameter DiT + 24 kHz Vocos vocoder, calibrated 6.5 mel frames/character duration model, standalone `vocab.txt`, static INT8 DiT export prototype at 349 MB, Vocos INT8 export at 22 MB, and custom native C++ engine `libindicf5_engine.so` with static memory arenas).
  3. **Phase 3 (Proposed Future Roadmap):** Sampling step distillation (2-step/4-step consistency reflow) and Google LiteRT compilation with vendor delegate offloading (Qualcomm QNN HTP, MediaTek NeuroPilot).
- **Figure 4.3 Validation:** The revised architecture diagram visually separates the C++/Dart FFI IndicF5 pipeline from the empirical ZipVoice baseline block ("Measured ZipVoice PoC Baseline [Empirical Reference]"), preventing any misattribution of ZipVoice metrics to the IndicF5 engine.

---

### 1.3 IndicF5 ONNX Sequence Dimensions and Runtime Status
- **Status:** **CONFIRMED & ACCURATELY DOCUMENTED**
- **Artifact Ground Truth:**
  - `indicf5_dit_fp32_static.onnx` (1.36 GB): Fixed 128 mel frames ($T=128$), used for numerical baseline parity testing.
  - `indicf5_dit_dynamic_fp32.onnx` (1.36 GB): Dynamic sequence dimensions, provides verified variable-length synthesis in desktop Python/ONNX Runtime environments.
  - `indicf5_dit_int8_static.onnx` (349 MB): Static INT8 post-training quantized graph with fixed 128-frame tensor dimensions ($T=128$), exported as an optimization prototype to validate integer quantization stability and static memory arena sizing.
  - `indicf5_vocos_int8.onnx` (22 MB): INT8 quantized Vocos vocoder.
- **Clarification of Variable-Length Inference:**
  - A 3.5-second reference audio clip alone requires $\approx 328$ mel frames at 24 kHz ($H=256$).
  - Naive temporal chunking cannot be applied because F5-TTS relies on bidirectional cross-attention with RoPE across the entire concatenated prompt-and-target sequence; chunking into isolated 128-frame blocks would sever acoustic conditioning.
  - Variable-length synthesis is currently verified using the dynamic FP32 ONNX graph on desktop hosts.
  - Dynamic-axis INT8 mobile compilation is explicitly designated as the post-midsem integration milestone.
  - The C++ engine (`libindicf5_engine.so`) currently validates session initialization and static arena allocation using the 128-frame static INT8 prototype.

---

### 1.4 Analytical Character of the 801 MB Memory Budget
- **Status:** **CONFIRMED & STRICTLY QUALIFIED**
- Table 4.3 preserves the exact calculated component breakdown:
  - Quantized DiT weights: **349 MB**
  - Quantized Vocos weights: **22 MB**
  - Pre-allocated working arenas: **280 MB**
  - Flutter / Dart VM runtime: **150 MB**
  - **Analytical Component Total:** **801 MB**
- **Presentation Corrections:**
  - Removed "Nominal LowMemoryKiller Pressure Threshold: 1500–1800 MB". Replaced with **"Engineering Planning Reference Target: $\approx 1,500$ MB (Nominal Edge Budget)"**.
  - Removed "+699 MB Analytical Margin (Feasible Target)". Replaced with **"Within Planning Target ($-699$ MB Target Margin)"**.
  - Added preferred qualifying language across all chapters: *"The proposed quantized architecture has an analytical component budget of approximately 801 MB; its actual process memory footprint remains subject to validation on target Android hardware."*
  - Explicitly clarified that actual process RSS can differ due to dynamic heap allocations, memory-mapped weights, intermediate tensor activations, shared libraries, and OS memory allocator behavior.

---

### 1.5 Diagram and Visual Layout Validation
- **Status:** **CONFIRMED & VECTOR RENDERED**
- All figures are generated as clean vector PDFs:
  - `Figures/system_architecture.pdf` (Figure 3.1)
  - `Figures/indicf5_pipeline.pdf` (Figure 3.2)
  - `Figures/lenovo_rtf.pdf` (Figure 4.1)
  - `Figures/lenovo_vmrss.pdf` (Figure 4.2)
  - `Figures/runtime_architecture.pdf` (Figure 4.3, updated per Task 2)
  - `Figures/optimization_roadmap.pdf` (Figure 5.1)
- **Float Layout (Task 8):** Table 4.1 and Table 4.2 sit together on Report Page 36 (PDF Page 45); Figure 4.1 and Figure 4.2 sit on Report Page 37 (PDF Page 46). Neither page is cramped, and text labels are crisp at 100% zoom.
- **List of Figures / List of Tables (Task 11.4):** Each fits cleanly on exactly one page (Page 8 and Page 9). The empty continuation page ix has been eliminated.

---

### 1.6 Bibliography Corrections
- **Status:** **CONFIRMED & PRIMARY SOURCED**
  - **Reference [4] (E2 TTS):** Verified author list starting with Sefik Emre Eskimez et al. (arXiv:2406.18009, 2024).
  - **Reference [15] (FlashSpeech):** Verified author list: Zhen Ye, Wei Xue, Xu Tan, Qifeng Chen, Yike Guo (arXiv:2404.14700, 2024). Speculative 2-step physical roles removed from §5.5.2.
  - **Reference [19] (ONNX Runtime Mobile):** Verified Microsoft Corporation official documentation URL.
  - All 23 citations map to verified publications or repositories.

---

### 1.7 Abstract and Privacy Claims
- **Status:** **CONFIRMED & STRICTLY QUALIFIED**
- Replaced absolute security claims with: *"Performing inference entirely on-device avoids the need to transmit biometric voice recordings to external inference services, reducing network-related privacy exposure."*
- Abstract layout strictly preserved on Roman page `i` (Page 2).

---

### 1.8 Final Micro-Fix Pass Validations
- **Fix 1 (§4.11.2, PDF Page 53):** Truncated ONNX filenames in the `Ort::Session` bullet were replaced with concise text referencing the fixed-shape INT8 DiT prototype and quantized Vocos vocoder. Text fits cleanly within margins with 0 overfull hboxes.
- **Fix 2 (§3.1, PDF Page 32):** Phase 2 runtime bullet was updated to distinguish the fixed-shape INT8 ONNX optimization prototype and the dynamic-axis FP32 ONNX graph, in full agreement with §§4.10–4.11.
- **Fix 3 (§2.1.2, PDF Page 20):** Duplicated VAE acronym expansion (`Conditional Variational Autoencoders (\glspl{vae})`) was replaced with `Conditional variational autoencoders (VAEs)`. Additionally, `\glspl{npu}` in §5.1 was replaced with `\acrshort{npu}s`.
- **Fix 4 (§4.7.3, PDF Page 50):** The reference duration statement was softened from an absolute "law" to: *"Based on preliminary synthesis experiments, we recommend reference audio clips between 3.5 and 5.0 seconds for the evaluated IndicF5 configuration..."*. Titles in §3.4 and §6.1 were correspondingly calibrated.

---

## 2. Items Verified vs. Documented as Planned Milestones

| Feature / Metric | Status in Project Evidence | Presentation in Report |
|---|---|---|
| ZipVoice Android Flutter Prototype | Implemented & Measured (`voice_clone_proto`) | Reported as implemented PoC baseline with full empirical benchmarks |
| Lenovo Tab K10 Physical Benchmarks | 9 trials measured from kernel (`/proc/self/status`) | Reported as measured arithmetic means and trial ranges |
| Desktop IndicF5 PyTorch Pipeline | Implemented & Tested (`clone.py`, `batch.py`) | Reported as desktop verification milestone across 4 Indic languages |
| Calibrated Duration Constant (6.5 frames/char) | Implemented & Calibrated | Formulated in §4.6 and Appendix B |
| FP32 Static ONNX Graph (128 frames) | Present in `models/indicf5/` (1.36 GB) | Reported as static baseline parity artifact |
| FP32 Dynamic ONNX Graph | Present in `models/indicf5/` (1.36 GB) | Reported as verified desktop variable-length inference engine |
| INT8 Static ONNX DiT Graph (128 frames) | Present in `models/indicf5/` (349 MB) | Reported as INT8 quantization & static arena export prototype |
| INT8 Vocos Vocoder Graph | Present in `models/indicf5/` (22 MB) | Reported as INT8 neural vocoder export artifact |
| Native C++ Engine (`libindicf5_engine.so`) | Engineered via ONNX Runtime Mobile C++ API | Reported as native loading & static arena management interface |
| Variable-length on-device INT8 inference | Not yet compiled with dynamic axes | Documented as immediate post-midsem integration milestone |
| Google LiteRT Compilation (`indicf5_dit_int8.tflite`) | Planned post-midsem | Formally presented in Chapter 5 as future architectural roadmap |
| NPU Delegate Acceleration (QNN HTP / NeuroPilot) | Planned post-midsem (compatible hardware only) | Explicitly marked as proposed and hardware-dependent |
| FlashSpeech 2-Step Consistency Distillation | Planned post-midsem | Formulated in §5.5.2 as planned trajectory distillation |

---

## 3. Submission Readiness Confirmation

- [x] Zero compilation errors (Tectonic exited with code `0`).
- [x] Exactly 75 pages matching reference report structure.
- [x] No visible TODO markers, draft notes, or speculative claims.
- [x] Mathematical proofs, Unicode multilingual prompt datasets, and architectural diagrams fully preserved.
- [x] All deliverables ready for immediate academic submission.
