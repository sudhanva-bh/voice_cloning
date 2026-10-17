# VALIDATION NOTES: Post-Midsem Engineering & Empirical Verification Tracker

**Project Title:** On-Device Indic Voice Cloning and Text-to-Speech Synthesis for Edge Architectures  
**Course:** CS F377 Design Project  
**Author:** Sudhanva B H  
**Document Purpose:** Internal Engineering Record of Outstanding Validation Items  
*(Note: These notes are maintained outside the submitted PDF report. Outstanding experiments are framed naturally as limitations and future work within the academic text.)*

---

## 1. High-Priority Validation Gaps (Immediate Post-Midsem Work)

### 1.1 Physical On-Device Profiling of Native IndicF5 on Lenovo Tab K10
* **Status at Mid-Semester:** 
  * The ZipVoice-Distill PoC was thoroughly instrumented and benchmarked on physical hardware across four silicon tiers, including nine full trials on the Lenovo Tab K10.
  * The primary IndicF5 pipeline was ported, validated on desktop, exported to INT8 ONNX, and wrapped in a custom native C++ engine with pre-allocated static arenas.
* **Validation Gap:** Physical on-device execution benchmarks (RTF, memory, thermal throttling) for the native IndicF5 C++ engine on the physical Lenovo Tab K10 have not yet been logged.
* **Target Milestone:** Deploy `libindicf5_engine.so` to the Android prototype on the Tab K10 and execute multi-sentence runs from `prompts.json` to record actual on-device latency and resident memory.

### 1.2 Dynamic Sequence Support for Quantized IndicF5
* **Status at Mid-Semester:**
  * Two FP32 ONNX graphs were exported: `indicf5_dit_fp32_static.onnx` (fixed at 128 mel frames) and `indicf5_dit_dynamic_fp32.onnx` (dynamic sequence dimensions).
  * The static INT8 quantized graph (`indicf5_dit_int8_static.onnx`, 349 MB) was compiled with fixed 128-frame tensor dimensions to test static memory arena allocation.
* **Validation Gap:** A standard 3.5-second reference audio alone spans $\approx 328$ mel frames (at 24 kHz, hop 256). Fixed 128-frame graphs cannot ingest full classroom reference clips without dynamic axes or chunked processing.
* **Target Milestone:** Finalize post-training quantization with dynamic sequence dimensions in ONNX Runtime Mobile or LiteRT Torch to support variable-length reference and target sequences.

### 1.3 Fine-Grained Transient Memory Profiling
* **Status at Mid-Semester:**
  * The reported Lenovo Tab K10 readings represent post-utterance resident memory (`VmRSS`) sampled from `/proc/self/status` immediately after audio synthesis completes.
* **Validation Gap:** Post-utterance sampling measures residual resident memory but does not capture peak transient allocations occurring during the intermediate Euler integration steps.
* **Target Milestone:** Implement continuous sampling at 50 ms intervals via a background daemon thread during synthesis to capture true peak RSS and memory allocation profiles.

---

## 2. Medium-Priority Validation Gaps (Acoustic Quality & Linguistic Evaluation)

### 2.1 Quantitative Speech Quality and Intelligibility Metrics
* **Status at Mid-Semester:** Synthesized audio across Tamil, Telugu, Kannada, and Hindi was verified for phonetic intelligibility and natural cadence through subjective developer listening tests.
* **Validation Gap:** No formal objective metrics (Word Error Rate via Whisper/Wav2Vec2, Character Error Rate, Perceptual Evaluation of Speech Quality / PESQ, or Mean Opinion Scores) have been computed.
* **Target Milestone:** Conduct a formal evaluation across all 120 phrases in `prompts.json`, reporting WER and CER across FP32 PyTorch baseline vs. INT8 quantized ONNX graphs across $N \in \{2, 4, 8, 16\}$ sampling steps.

### 2.2 Deep Speaker Embedding Similarity
* **Status at Mid-Semester:** Zero-shot timbre replication was demonstrated subjectively using voice reference samples (`sudhanva_short_ref.wav` and regional prompts).
* **Validation Gap:** No quantitative cosine similarity scores using deep speaker verification models (e.g., ECAPA-TDNN, WavLM, or Resemblyzer) have been published.
* **Target Milestone:** Compute cosine distance distributions between reference speech embeddings and synthesized target speech embeddings across registered speaker profiles.

### 2.3 Acoustic Robustness to Classroom Noise
* **Status at Mid-Semester:** Reference audio clips were recorded under relatively clean conditions using smartphones and studio microphones.
* **Validation Gap:** Real-world government school classrooms present ambient noise, room reverberation, child chatter, and mobile microphone distortion.
* **Target Milestone:** Evaluate voice cloning degradation under controlled signal-to-noise ratios (SNR 10 dB to 25 dB) and evaluate whether speech enhancement preprocessing (e.g., DTLN or RNNoise) is necessary prior to mel extraction.

---

## 3. Low-Priority Validation Gaps (Future Roadmap & Hardware Delegates)

### 3.1 LiteRT Torch Conversion Parity
* **Status at Mid-Semester:** The Google LiteRT transition is designed and documented in Chapter 5, including Python export listings and StableHLO operator fusion theory.
* **Validation Gap:** The actual `.tflite` FlatBuffer export via `litert-torch` has not yet been executed in the project workspace.
* **Target Milestone:** Execute `litert-torch.convert()` on the IndicF5 PyTorch backbone, serialize `indicf5_dit_int8.tflite`, and verify numerical equivalence against FP32 tensors (MCD $< 3.5$ dB).

### 3.2 NPU Delegate Offloading on Compatible Silicon
* **Status at Mid-Semester:** The report clarifies that the Helio P22T lacks an NPU and relies on CPU XNNPACK, while QNN HTP and NeuroPilot are roadmap targets for compatible hardware.
* **Validation Gap:** On-device delegate execution times and operator partition percentages on Snapdragon 8 Gen 2 (Galaxy S23) and Dimensity (Galaxy M53) are analytical projections.
* **Target Milestone:** Compile and profile LiteRT delegate binaries on Snapdragon hardware using the Qualcomm AI Engine Direct profiling tools to verify that 100% of DiT attention and linear layers execute on the Hexagon Tensor Processor.
