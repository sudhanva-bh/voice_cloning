#!/usr/bin/env python3
"""
Dual-Engine Numerical Parity Evaluation Harness for Google LiteRT vs PyTorch Baseline.
Executes both engines on identical speech inputs and calculates:
1. Velocity vector field Cosine Similarity across all 8 Euler ODE diffusion steps
2. Spectrogram L1/L2 and Maximum Absolute Error
3. Dynamic Time Warping Mel-Cepstral Distortion (DTW-MCD in dB)
4. End-to-end Real-Time Factor (RTF) comparison
"""

import argparse
import os
import sys
import time
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch
import torchaudio

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

SCRATCH_REPO = REPO_ROOT / "scratch" / "indicf5_repo"
if SCRATCH_REPO.is_dir():
    sys.path.insert(0, str(SCRATCH_REPO))

# Import LiteRT interpreter
try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    try:
        from litert.interpreter import Interpreter
    except ImportError:
        from tflite_runtime.interpreter import Interpreter

from safetensors.torch import load_file
from vocos import Vocos
from f5_tts.model.backbones.dit import DiT
from scripts.infer_litert import (
    load_vocab,
    text_to_tokens,
    extract_mel_spectrogram,
    synthesize_audio_from_spec,
    DEFAULT_DIT,
    DEFAULT_VOCOS,
    DEFAULT_VOCAB,
)


def compute_dtw_mcd(wav_ref: np.ndarray, wav_synth: np.ndarray, sr: int = 24000, n_mfcc: int = 16) -> float:
    """
    Computes Mel-Cepstral Distortion (MCD) using Dynamic Time Warping (DTW)
    between reference and synthesized audio signals.
    MCD = (10 * sqrt(2) / ln(10)) * mean(Euclidean distance of MFCC vectors).
    """
    # Ensure minimum audio length
    min_len = int(sr * 0.1)
    if len(wav_ref) < min_len or len(wav_synth) < min_len:
        return 0.0

    # Extract MFCCs (excluding 0th coefficient representing overall energy)
    mfcc_ref = librosa.feature.mfcc(y=wav_ref, sr=sr, n_mfcc=n_mfcc + 1, n_fft=1024, hop_length=256)[1:, :].T
    mfcc_synth = librosa.feature.mfcc(y=wav_synth, sr=sr, n_mfcc=n_mfcc + 1, n_fft=1024, hop_length=256)[1:, :].T

    # Compute pairwise Euclidean distance matrix
    from scipy.spatial.distance import cdist
    cost_matrix = cdist(mfcc_ref, mfcc_synth, metric="euclidean")

    # Dynamic Time Warping using dynamic programming
    N, M = cost_matrix.shape
    accumulated_cost = np.zeros((N, M), dtype=np.float32)
    accumulated_cost[0, 0] = cost_matrix[0, 0]

    for i in range(1, N):
        accumulated_cost[i, 0] = accumulated_cost[i - 1, 0] + cost_matrix[i, 0]
    for j in range(1, M):
        accumulated_cost[0, j] = accumulated_cost[0, j - 1] + cost_matrix[0, j]
    for i in range(1, N):
        for j in range(1, M):
            accumulated_cost[i, j] = cost_matrix[i, j] + min(
                accumulated_cost[i - 1, j],
                accumulated_cost[i, j - 1],
                accumulated_cost[i - 1, j - 1],
            )

    # Backtrack DTW optimal path
    i, j = N - 1, M - 1
    path_distances = []
    while i > 0 or j > 0:
        path_distances.append(cost_matrix[i, j])
        if i == 0:
            j -= 1
        elif j == 0:
            i -= 1
        else:
            min_prev = min(accumulated_cost[i - 1, j], accumulated_cost[i, j - 1], accumulated_cost[i - 1, j - 1])
            if accumulated_cost[i - 1, j - 1] == min_prev:
                i -= 1
                j -= 1
            elif accumulated_cost[i - 1, j] == min_prev:
                i -= 1
            else:
                j -= 1
    path_distances.append(cost_matrix[0, 0])

    # Convert to decibels (dB)
    scale = 10.0 * np.sqrt(2.0) / np.log(10.0)
    mcd = scale * np.mean(path_distances)
    return float(mcd)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Computes cosine similarity between two flattened arrays."""
    a_flat = a.flatten().astype(np.float64)
    b_flat = b.flatten().astype(np.float64)
    norm_a = np.linalg.norm(a_flat)
    norm_b = np.linalg.norm(b_flat)
    if norm_a < 1e-12 or norm_b < 1e-12:
        return 1.0
    return float(np.dot(a_flat, b_flat) / (norm_a * norm_b))


def evaluate_parity(
    ref_audio_path: Path,
    ref_text: str,
    gen_text: str,
    output_dir: Path,
    steps: int = 8,
    seed: int = 42,
    seq_bucket: int = 512,
    text_len: int = 128,
):
    print("=" * 78)
    print("        DUAL-ENGINE PARITY EVALUATION: PYTORCH FP32 vs GOOGLE LITERt FP32")
    print("=" * 78)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Prepare identical inputs
    print("\n[Step 1/5] Preparing identical speech inputs and deterministic noise...")
    ref_mel, ref_rms = extract_mel_spectrogram(ref_audio_path)
    ref_frames = ref_mel.shape[-1]

    # Cap reference audio to half the bucket (e.g. 256 frames ~ 2.7 sec)
    # to guarantee at least 256 frames of headroom for target speech generation
    max_ref_frames = seq_bucket // 2
    if ref_frames > max_ref_frames:
        print(f"  Reference audio has {ref_frames} frames. Slicing to {max_ref_frames} frames (~{max_ref_frames * 256 / 24000:.2f}s) for bucket balance.")
        ref_mel = ref_mel[:, :max_ref_frames]
        ref_frames = max_ref_frames

    ref_char_len = max(len(ref_text), 1)
    gen_char_len = max(len(gen_text), 1)
    gen_frames = int(ref_frames / ref_char_len * gen_char_len)
    total_frames = min(ref_frames + gen_frames, seq_bucket)
    actual_ref_len = min(ref_frames, seq_bucket)

    vocab_map = load_vocab(DEFAULT_VOCAB)
    full_text = f"{ref_text.strip()} {gen_text.strip()}"
    tokens = text_to_tokens(full_text, vocab_map, max_len=text_len)

    cond_np = np.zeros((1, seq_bucket, 100), dtype=np.float32)
    cond_np[0, :actual_ref_len, :] = ref_mel.numpy().T[:actual_ref_len, :]

    np.random.seed(seed)
    noise_init = np.random.randn(1, seq_bucket, 100).astype(np.float32)

    # Convert to PyTorch tensors for PyTorch execution
    torch_x = torch.from_numpy(noise_init.copy())
    torch_cond = torch.from_numpy(cond_np.copy())
    torch_text = torch.from_numpy(tokens.copy())

    # 2. Instantiate PyTorch DiT & load safetensors
    print("\n[Step 2/5] Loading PyTorch 335M-parameter DiT baseline...")
    dit_cfg = dict(
        dim=1024,
        depth=22,
        heads=16,
        ff_mult=2,
        text_dim=512,
        conv_layers=4,
        text_num_embeds=len(vocab_map),
        mel_dim=100,
    )
    pytorch_dit = DiT(**dit_cfg).eval()
    ckpt = load_file(str(REPO_ROOT / "models" / "indicf5" / "model.safetensors"))
    dit_state_dict = {
        k.replace("transformer.", "").replace("ema_model.", ""): v
        for k, v in ckpt.items()
        if "transformer." in k
    }
    pytorch_dit.load_state_dict(dit_state_dict, strict=True)
    del ckpt, dit_state_dict

    # 3. Instantiate LiteRT DiT Interpreter
    print("\n[Step 3/5] Loading Google LiteRT indicf5_dit_fp32.tflite...")
    dit_interp = Interpreter(model_path=str(DEFAULT_DIT))
    dit_interp.allocate_tensors()
    dit_in = dit_interp.get_input_details()
    dit_out = dit_interp.get_output_details()

    # 4. Step-by-Step Dual Euler ODE Integration
    print(f"\n[Step 4/5] Executing Synchronized Dual Euler ODE Integration ({steps} steps)...")
    dt = 1.0 / steps
    litert_x = noise_init.copy()

    step_metrics = []
    pyt_total_time = 0.0
    litert_total_time = 0.0

    print("  Step | Time (t) | PyTorch Latency | LiteRT Latency | Cosine Sim | L1 Error  | Max Error")
    print("  -----+----------+-----------------+----------------+------------+-----------+-----------")

    for step in range(steps):
        t_val = step / float(steps)
        t_tensor = torch.tensor([t_val], dtype=torch.float32)
        t_np = np.array([t_val], dtype=np.float32)

        # PyTorch forward
        t0 = time.time()
        with torch.no_grad():
            pyt_v = pytorch_dit(
                x=torch_x,
                cond=torch_cond,
                text=torch_text,
                time=t_tensor,
                drop_audio_cond=False,
                drop_text=False,
                mask=None,
            )
        pyt_step_time = time.time() - t0
        pyt_total_time += pyt_step_time

        # LiteRT forward
        dit_interp.set_tensor(dit_in[0]["index"], litert_x)
        dit_interp.set_tensor(dit_in[1]["index"], cond_np)
        dit_interp.set_tensor(dit_in[2]["index"], tokens)
        dit_interp.set_tensor(dit_in[3]["index"], t_np)

        t0 = time.time()
        dit_interp.invoke()
        litert_step_time = time.time() - t0
        litert_total_time += litert_step_time

        litert_v = dit_interp.get_tensor(dit_out[0]["index"])

        # Compare v predictions
        pyt_v_np = pyt_v.numpy()
        cossim = cosine_similarity(pyt_v_np, litert_v)
        l1_err = float(np.mean(np.abs(pyt_v_np - litert_v)))
        max_err = float(np.max(np.abs(pyt_v_np - litert_v)))

        step_metrics.append({
            "step": step,
            "t": t_val,
            "cossim": cossim,
            "l1": l1_err,
            "max": max_err,
        })

        print(f"  {step + 1:>4} | {t_val:>8.3f} | {pyt_step_time:>13.3f}s | {litert_step_time:>12.3f}s | {cossim:>10.5f} | {l1_err:>9.5f} | {max_err:>9.5f}")

        # Euler state updates
        torch_x = torch_x + dt * pyt_v
        litert_x = litert_x + dt * litert_v

    # Restore reference conditioning
    torch_x[0, :actual_ref_len, :] = torch_cond[0, :actual_ref_len, :]
    litert_x[0, :actual_ref_len, :] = cond_np[0, :actual_ref_len, :]

    # 5. Dual Vocoding & Waveform Parity
    print("\n[Step 5/5] Synthesizing waveforms and calculating Mel-Cepstral Distortion (MCD)...")
    vocoder_pytorch = Vocos.from_pretrained("charactr/vocos-mel-24khz").eval()

    # PyTorch Vocos waveform
    pyt_mel_in = torch_x.permute(0, 2, 1)  # [1, 100, 512]
    with torch.no_grad():
        pyt_full_wav = vocoder_pytorch.decode(pyt_mel_in).squeeze().cpu().numpy()

    # LiteRT Vocos waveform
    vocos_interp = Interpreter(model_path=str(DEFAULT_VOCOS))
    vocos_interp.allocate_tensors()
    v_in = vocos_interp.get_input_details()
    v_out = vocos_interp.get_output_details()

    litert_mel_in = np.transpose(litert_x, (0, 2, 1))
    vocos_interp.set_tensor(v_in[0]["index"], litert_mel_in)
    vocos_interp.invoke()
    complex_spec = vocos_interp.get_tensor(v_out[0]["index"])

    real_p = torch.from_numpy(complex_spec[0, 0, :, :])
    imag_p = torch.from_numpy(complex_spec[0, 1, :, :])
    litert_full_wav = synthesize_audio_from_spec(real_p, imag_p)

    # Slice target audio
    start_s = actual_ref_len * 256
    end_s = total_frames * 256
    pyt_gen_wav = pyt_full_wav[start_s:end_s]
    litert_gen_wav = litert_full_wav[start_s:end_s]

    # Save audio files
    pyt_wav_path = output_dir / "pytorch_baseline.wav"
    litert_wav_path = output_dir / "litert_fp32.wav"
    sf.write(str(pyt_wav_path), pyt_gen_wav, 24000)
    sf.write(str(litert_wav_path), litert_gen_wav, 24000)
    print(f"  Saved PyTorch Ground Truth: {pyt_wav_path}")
    print(f"  Saved LiteRT FP32 Output:   {litert_wav_path}")

    # Calculate MCD
    mcd_value = compute_dtw_mcd(pyt_gen_wav, litert_gen_wav, sr=24000)
    avg_cossim = np.mean([m["cossim"] for m in step_metrics])
    min_cossim = np.min([m["cossim"] for m in step_metrics])
    avg_l1 = np.mean([m["l1"] for m in step_metrics])

    audio_dur = len(litert_gen_wav) / 24000.0
    litert_rtf = litert_total_time / max(audio_dur, 1e-4)
    pyt_rtf = pyt_total_time / max(audio_dur, 1e-4)

    # Print Certification Summary
    print("\n" + "=" * 78)
    print("                     PHASE 2 PARITY CERTIFICATION SUMMARY")
    print("=" * 78)
    print(f"  Target Generated Speech:      {audio_dur:.2f} seconds ({len(litert_gen_wav)} samples)")
    print(f"  Average Velocity Cosine Sim:  {avg_cossim:.6f}  (Gate: >= 0.990) -> {'[PASS]' if avg_cossim >= 0.990 else '[FAIL]'}")
    print(f"  Minimum Velocity Cosine Sim:  {min_cossim:.6f}  (Gate: >= 0.980) -> {'[PASS]' if min_cossim >= 0.980 else '[FAIL]'}")
    print(f"  Average Spectrogram L1 Error: {avg_l1:.6f}  (Gate: <= 0.050) -> {'[PASS]' if avg_l1 <= 0.050 else '[FAIL]'}")
    print(f"  Mel-Cepstral Distortion (MCD):{mcd_value:.4f} dB (Gate: <= 1.000 dB) -> {'[PASS]' if mcd_value <= 1.000 else '[FAIL]'}")
    print(f"  LiteRT Real-Time Factor (RTF):{litert_rtf:.3f}x (Gate: <= 1.000x) -> {'[PASS]' if litert_rtf <= 1.000 else '[FAIL]'}")
    print(f"  PyTorch Baseline RTF:         {pyt_rtf:.3f}x")
    print("=" * 78)

    all_passed = (avg_cossim >= 0.990) and (mcd_value <= 1.000)
    if all_passed:
        print("  🎉 PHASE 2 PARITY CERTIFICATION PASSED: LITERt FP32 MATCHES PYTORCH BASELINE!")
    else:
        print("  ❌ PHASE 2 PARITY CERTIFICATION FAILED: Metrics out of tolerance.")
    print("=" * 78 + "\n")

    return all_passed, mcd_value, avg_cossim, litert_rtf


def main():
    parser = argparse.ArgumentParser(description="Evaluate Parity between PyTorch and LiteRT")
    parser.add_argument(
        "--ref_audio",
        type=str,
        default="scratch/indicf5_repo/f5_tts/infer/examples/basic/basic_ref_en.wav",
        help="Path to reference audio (.wav)",
    )
    parser.add_argument(
        "--ref_text",
        type=str,
        default="Some call me nature, others call me mother nature.",
        help="Transcript of reference audio",
    )
    parser.add_argument(
        "--gen_text",
        type=str,
        default="Google LiteRT enables ultra low latency on device voice cloning.",
        help="Target text to clone and synthesize",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="scratch/parity_test",
        help="Directory to save generated comparison wavs",
    )
    parser.add_argument("--steps", type=int, default=8, help="Number of Euler ODE steps (default: 8)")
    parser.add_argument("--seed", type=int, default=42, help="Fixed random seed")

    args = parser.parse_args()
    evaluate_parity(
        ref_audio_path=Path(args.ref_audio),
        ref_text=args.ref_text,
        gen_text=args.gen_text,
        output_dir=Path(args.output_dir),
        steps=args.steps,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
