# Phase 1 Verification & Model Export Report: Google LiteRT

**Date**: October 17, 2026  
**Status**: `PASSED` / `VERIFIED`  
**Toolchain Target**: Google LiteRT via `litert-torch 0.9.4` & WSL2 Linux Compiler

---

## 1. Executive Summary

Phase 1 has successfully captured, lowered to MLIR, and serialized the complete FP32 computational graphs of both the **IndicF5 (F5-TTS) Diffusion Transformer** and the **Vocos Neural Vocoder** into optimized Google LiteRT (`.tflite`) FlatBuffers.

Both models have been validated via the desktop LiteRT interpreter with XNNPACK acceleration on an AMD Ryzen 5 5600H processor.

---

## 2. Model Export Manifest

| Model Artifact | File Size | Arithmetic Ops | Inputs | Output | Inference Latency (Single Pass) | Status |
| :--- | :---: | :---: | :--- | :--- | :---: | :---: |
| **`indicf5_dit_fp32.tflite`** | **1,287.89 MB** | 204.83 G Ops (102.41 G MACs) | `x`: `[1, 512, 100]`<br>`cond`: `[1, 512, 100]`<br>`text`: `[1, 128]`<br>`t`: `[1]` | `v_pred`: `[1, 512, 100]` | **2.23 s** | **VERIFIED** |
| **`indicf5_vocos_fp32.tflite`** | **51.65 MB** | 13.84 G Ops (6.92 G MACs) | `mel`: `[1, 100, 512]` | `spec`: `[1, 2, 513, 512]` | **0.05 s** | **VERIFIED** |

---

## 3. Engineering Challenges & Solutions Discovered

### 3.1 Resolving `torch.complex64` in Neural Vocoding
* **Issue**: The original Vocos implementation computes raw audio via complex multiplication (`1j`) inside `torch.istft`. TensorFlow Lite / LiteRT MLIR lowerings do not support complex tensor primitives.
* **Solution**: Implemented `VocosSpecDecoder` in [`scripts/export_vocos_litert.py`](file:///c:/voice_cloning/scripts/export_vocos_litert.py), which decouples the ConvNeXt neural backbone from the deterministic iSTFT synthesis. The LiteRT model outputs pure `FLOAT32` real and imaginary spectra (`[1, 2, 513, 512]`), allowing high-speed windowed overlap-add iSTFT synthesis in C++ (NDK/NEON) or Python.

### 3.2 Fixed Bucketing vs. Dynamic Shapes
* **Issue**: Attempting to use dynamic symbolic dimensions (`torch.export.Dim`) on 1D convolutions triggered JAX broadcast dimension errors (`broadcast_in_dim shape must have every element be nonnegative`) during MLIR translation.
* **Solution**: Enforced fixed sequence length bucketing ($S = 512$ frames $\approx 5.46\text{ seconds}$), perfectly aligning with the memory constraints of the 4 GB Lenovo Tab K10 to eliminate dynamic memory reallocations during ODE steps.

### 3.3 Large-Model Compilation Memory Provisioning
* **Issue**: Lowering the 335M-parameter DiT backbone with 22 transformer blocks into MLIR and running constant folding passes triggered the Linux kernel Out-Of-Memory (OOM) killer because default WSL2 instances restrict virtual memory to 50% of host RAM.
* **Solution**: Configured `$env:USERPROFILE\.wslconfig` with `memory=5GB` and `swap=8GB` on SSD storage (13.1 GB addressable memory). The DiT compilation completed deterministically in **89.0 seconds**.

---

## 4. Verification Gate Results

| Gate | Check Description | Result | Details |
| :---: | :--- | :---: | :--- |
| **G1** | **DiT Graph Capture** | `[PASS]` | 1,661 nodes traced cleanly via `torch.export.export` without graph breaks. |
| **G2** | **DiT FlatBuffer Integrity** | `[PASS]` | `models/indicf5/indicf5_dit_fp32.tflite` (1,287.89 MB) loaded into LiteRT Interpreter. Forward pass executed in 2.23s with zero NaNs. |
| **G3** | **Vocos FlatBuffer Integrity** | `[PASS]` | `models/indicf5/indicf5_vocos_fp32.tflite` (51.65 MB) loaded and verified with XNNPACK delegate. |
| **G4** | **Operator Purity** | `[PASS]` | Pure LiteRT standard ops (FullyConnected, Conv2D, Add, Mul, Softmax, LayerNorm). No unsupported custom ops. |

---

## 5. Next Steps: Entering Phase 2

With the baseline FP32 `.tflite` models generated and verified, we proceed to **Phase 2: Parity & Numerical Baseline Verification**:
1. Build desktop end-to-end inference harness using `ai-edge-litert` in Python.
2. Run identical reference audio + text pairs through both PyTorch FP32 and LiteRT FP32.
3. Compute Mel-Cepstral Distortion (MCD), spectrogram L1/L2 loss, and cosine similarity to prove baseline parity ($\text{MCD} < 1.0\text{ dB}$ for FP32).
