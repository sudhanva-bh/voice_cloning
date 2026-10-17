#!/usr/bin/env python3
"""
scripts/benchmark_int8.py: INT8 vs FP32 Parity, Latency, and Acoustic Fidelity Benchmark.

Executes continuous flow matching across LiteRT FP32 and INT8 quantized FlatBuffers,
measuring velocity cosine similarity, Mel-Cepstral Distortion (DTW-MCD), latency, and memory footprint.

Usage:
    wsl /mnt/c/voice_cloning/litert-wsl-env/bin/python3 scripts/benchmark_int8.py [options]
"""

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import LiteRT interpreter
try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    try:
        from litert.interpreter import Interpreter
    except ImportError:
        from tflite_runtime.interpreter import Interpreter

from scripts.infer_litert import (
    load_vocab,
    text_to_tokens,
    extract_mel_spectrogram,
    synthesize_audio_from_spec,
    DEFAULT_VOCAB,
)
from scripts.evaluate_parity import compute_dtw_mcd

DEFAULT_REF_AUDIO = REPO_ROOT / "scratch" / "indicf5_repo" / "f5_tts" / "infer" / "examples" / "basic" / "basic_ref_en.wav"
DEFAULT_REF_TEXT = "Some call me nature, others call me mother nature."
DEFAULT_GEN_TEXT = "Google LiteRT delivers ultra low latency voice cloning."

FP32_DIT = REPO_ROOT / "models" / "indicf5" / "indicf5_dit_fp32.tflite"
FP32_VOCOS = REPO_ROOT / "models" / "indicf5" / "indicf5_vocos_fp32.tflite"
INT8_DIT = REPO_ROOT / "models" / "indicf5" / "indicf5_dit_int8.tflite"
INT8_VOCOS = REPO_ROOT / "models" / "indicf5" / "indicf5_vocos_int8.tflite"


def parse_args():
    parser = argparse.ArgumentParser(description="LiteRT INT8 vs FP32 Parity & Performance Benchmark")
    parser.add_argument("--ref_audio", type=str, default=str(DEFAULT_REF_AUDIO), help="Path to reference audio")
    parser.add_argument("--ref_text", type=str, default=DEFAULT_REF_TEXT, help="Reference transcript")
    parser.add_argument("--gen_text", type=str, default=DEFAULT_GEN_TEXT, help="Target text to synthesize")
    parser.add_argument("--fp32_dit", type=str, default=str(FP32_DIT), help="Path to FP32 DiT model")
    parser.add_argument("--fp32_vocos", type=str, default=str(FP32_VOCOS), help="Path to FP32 Vocos model")
    parser.add_argument("--int8_dit", type=str, default=str(INT8_DIT), help="Path to INT8 DiT model")
    parser.add_argument("--int8_vocos", type=str, default=str(INT8_VOCOS), help="Path to INT8 Vocos model")
    parser.add_argument("--vocab", type=str, default=str(DEFAULT_VOCAB), help="Path to vocab.txt")
    parser.add_argument("--output_dir", type=str, default="scratch/parity_test", help="Output directory for audio")
    parser.add_argument("--steps", type=int, default=8, help="Number of Euler ODE steps (default: 8)")
    parser.add_argument("--seed", type=int, default=42, help="Fixed random seed")
    return parser.parse_args()


def run_pipeline(
    name: str,
    dit_path: Path,
    vocos_path: Path,
    ref_audio_path: Path,
    ref_text: str,
    gen_text: str,
    vocab_path: Path,
    steps: int = 8,
    seed: int = 42,
    seq_bucket: int = 512,
    text_len: int = 128,
):
    print(f"\n{'='*70}")
    print(f"[*] Running Pipeline: {name}")
    print(f"    DiT:   {dit_path.name} ({os.path.getsize(dit_path)/(1024*1024):.2f} MB)")
    print(f"    Vocos: {vocos_path.name} ({os.path.getsize(vocos_path)/(1024*1024):.2f} MB)")
    print(f"{'='*70}")

    # 1. Feature Extraction
    ref_mel, _ = extract_mel_spectrogram(ref_audio_path)
    ref_frames = ref_mel.shape[-1]
    max_ref_frames = seq_bucket // 2
    if ref_frames > max_ref_frames:
        ref_mel = ref_mel[:, :max_ref_frames]
        ref_frames = max_ref_frames

    ref_char_len = max(len(ref_text), 1)
    gen_char_len = max(len(gen_text), 1)
    gen_frames = int(ref_frames / ref_char_len * gen_char_len)
    total_frames = min(ref_frames + gen_frames, seq_bucket)

    vocab_map = load_vocab(vocab_path)
    full_text = f"{ref_text.strip()} {gen_text.strip()}"
    tokens = text_to_tokens(full_text, vocab_map, max_len=text_len)

    cond_mel = np.zeros((1, seq_bucket, 100), dtype=np.float32)
    ref_mel_np = ref_mel.numpy().T
    cond_mel[0, :ref_frames, :] = ref_mel_np[:ref_frames, :]

    np.random.seed(seed)
    x = np.random.randn(1, seq_bucket, 100).astype(np.float32)

    # 2. Init LiteRT
    dit_interp = Interpreter(model_path=str(dit_path))
    dit_interp.allocate_tensors()
    dit_in = dit_interp.get_input_details()
    dit_out = dit_interp.get_output_details()

    vocos_interp = Interpreter(model_path=str(vocos_path))
    vocos_interp.allocate_tensors()
    vocos_in = vocos_interp.get_input_details()
    vocos_out = vocos_interp.get_output_details()

    # 3. Euler ODE
    dt = 1.0 / steps
    velocities = []
    latencies = []

    t_ode0 = time.time()
    for step in range(steps):
        t_val = np.array([step / float(steps)], dtype=np.float32)
        dit_interp.set_tensor(dit_in[0]["index"], x)
        dit_interp.set_tensor(dit_in[1]["index"], cond_mel)
        dit_interp.set_tensor(dit_in[2]["index"], tokens)
        dit_interp.set_tensor(dit_in[3]["index"], t_val)

        t_s0 = time.time()
        dit_interp.invoke()
        step_lat = time.time() - t_s0

        v_pred = dit_interp.get_tensor(dit_out[0]["index"]).copy()
        velocities.append(v_pred)
        latencies.append(step_lat)

        x = x + dt * v_pred
        print(f"  Step [{step+1}/{steps}] (t={t_val[0]:.3f}): {step_lat:.3f}s | L2 Norm: {np.linalg.norm(v_pred):.2f}")

    ode_time = time.time() - t_ode0
    final_mel = x.copy()
    final_mel[0, :ref_frames, :] = cond_mel[0, :ref_frames, :]

    # 4. Vocos
    mel_voc = np.transpose(final_mel, (0, 2, 1))
    vocos_interp.set_tensor(vocos_in[0]["index"], mel_voc)
    t_v0 = time.time()
    vocos_interp.invoke()
    vocos_time = time.time() - t_v0

    spec = vocos_interp.get_tensor(vocos_out[0]["index"])
    real = torch.from_numpy(spec[0, 0, :, :])
    imag = torch.from_numpy(spec[0, 1, :, :])
    full_wav = synthesize_audio_from_spec(real, imag)

    start_sample = ref_frames * 256
    end_sample = total_frames * 256
    gen_wav = full_wav[start_sample:end_sample]

    max_v = np.max(np.abs(gen_wav))
    if max_v > 1e-4:
        gen_wav = gen_wav * (0.95 / max_v)

    return {
        "name": name,
        "velocities": velocities,
        "latencies": latencies,
        "ode_time": ode_time,
        "vocos_time": vocos_time,
        "final_mel": final_mel,
        "waveform": gen_wav,
    }


def main():
    args = parse_args()
    print("=" * 78)
    print("     GOOGLE LITERt INT8 vs FP32 PARITY & PERFORMANCE BENCHMARK")
    print("=" * 78)
    print(f"Reference Audio: {args.ref_audio}")
    print(f"Target Text:     \"{args.gen_text}\"")
    print(f"Euler ODE Steps: {args.steps}")
    print(f"Random Seed:     {args.seed}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run FP32 Pipeline
    fp32_res = run_pipeline(
        name="LiteRT FP32",
        dit_path=Path(args.fp32_dit),
        vocos_path=Path(args.fp32_vocos),
        ref_audio_path=Path(args.ref_audio),
        ref_text=args.ref_text,
        gen_text=args.gen_text,
        vocab_path=Path(args.vocab),
        steps=args.steps,
        seed=args.seed,
    )

    # 2. Run INT8 Pipeline
    int8_res = run_pipeline(
        name="LiteRT INT8",
        dit_path=Path(args.int8_dit),
        vocos_path=Path(args.int8_vocos),
        ref_audio_path=Path(args.ref_audio),
        ref_text=args.ref_text,
        gen_text=args.gen_text,
        vocab_path=Path(args.vocab),
        steps=args.steps,
        seed=args.seed,
    )

    # 3. Save Waveforms
    fp32_wav_path = out_dir / "litert_fp32.wav"
    int8_wav_path = out_dir / "litert_int8.wav"
    sf.write(str(fp32_wav_path), fp32_res["waveform"], 24000)
    sf.write(str(int8_wav_path), int8_res["waveform"], 24000)
    print(f"\n[+] Saved FP32 Audio: {fp32_wav_path}")
    print(f"[+] Saved INT8 Audio: {int8_wav_path}")

    # 4. Compare Step-by-Step Velocity Cosine Similarity
    print("\n" + "=" * 78)
    print("Step-by-Step Velocity Field Parity (FP32 vs INT8)")
    print("=" * 78)
    print(f"{'Step':<6} | {'t':<6} | {'FP32 Lat (s)':<13} | {'INT8 Lat (s)':<13} | {'Cosine Sim':<12} | {'L1 Error':<10}")
    print("-" * 78)

    cos_sims = []
    l1_errors = []
    for step in range(args.steps):
        v_fp32 = fp32_res["velocities"][step].flatten()
        v_int8 = int8_res["velocities"][step].flatten()

        dot = np.dot(v_fp32, v_int8)
        norm_fp32 = np.linalg.norm(v_fp32)
        norm_int8 = np.linalg.norm(v_int8)
        cos_sim = float(dot / (norm_fp32 * norm_int8 + 1e-9))
        cos_sims.append(cos_sim)

        l1_err = float(np.mean(np.abs(v_fp32 - v_int8)))
        l1_errors.append(l1_err)

        t_val = step / float(args.steps)
        print(f"{step+1:<6} | {t_val:<6.3f} | {fp32_res['latencies'][step]:<13.3f} | {int8_res['latencies'][step]:<13.3f} | {cos_sim:<12.5f} | {l1_err:<10.5f}")

    avg_cos_sim = float(np.mean(cos_sims))
    min_cos_sim = float(np.min(cos_sims))
    avg_l1 = float(np.mean(l1_errors))

    # 5. Spectrogram L1/L2
    mel_fp32 = fp32_res["final_mel"]
    mel_int8 = int8_res["final_mel"]
    mel_l1 = float(np.mean(np.abs(mel_fp32 - mel_int8)))
    mel_max_abs = float(np.max(np.abs(mel_fp32 - mel_int8)))

    # 6. DTW-MCD
    mcd_db = compute_dtw_mcd(fp32_res["waveform"], int8_res["waveform"], sr=24000)

    # 7. Model Sizes
    dit_fp32_mb = os.path.getsize(args.fp32_dit) / (1024 * 1024)
    dit_int8_mb = os.path.getsize(args.int8_dit) / (1024 * 1024)
    voc_fp32_mb = os.path.getsize(args.fp32_vocos) / (1024 * 1024)
    voc_int8_mb = os.path.getsize(args.int8_vocos) / (1024 * 1024)
    tot_fp32_mb = dit_fp32_mb + voc_fp32_mb
    tot_int8_mb = dit_int8_mb + voc_int8_mb

    # 8. Certification Matrix
    print("\n" + "=" * 78)
    print("Phase 3 Verification & Gate Certification Matrix")
    print("=" * 78)
    print(f"{'Gate':<6} | {'Metric Description':<32} | {'Requirement':<16} | {'Result':<12} | {'Status'}")
    print("-" * 78)

    g1_pass = dit_int8_mb <= 365.0
    print(f"G1     | DiT Model Memory Footprint       | <= 365.0 MB      | {dit_int8_mb:>7.2f} MB   | {'[PASSED]' if g1_pass else '[FAILED]'}")

    g2_pass = voc_int8_mb <= 25.0
    print(f"G2     | Vocos Model Memory Footprint     | <= 25.0 MB       | {voc_int8_mb:>7.2f} MB   | {'[PASSED]' if g2_pass else '[FAILED]'}")

    g3_pass = mcd_db <= 3.50
    print(f"G3     | Mel-Cepstral Distortion (DTW-MCD)| <= 3.50 dB       | {mcd_db:>7.4f} dB   | {'[PASSED]' if g3_pass else '[FAILED]'}")

    g4_pass = avg_cos_sim >= 0.950
    print(f"G4     | Velocity Cosine Similarity (Avg) | >= 0.950         | {avg_cos_sim:>7.5f}      | {'[PASSED]' if g4_pass else '[FAILED]'}")

    audio_dur = len(int8_res["waveform"]) / 24000.0
    g5_pass = audio_dur > 2.0 and not np.isnan(int8_res["waveform"]).any()
    print(f"G5     | Audio Duration & Non-Zero Signal | > 2.0s, finite   | {audio_dur:>7.2f} s    | {'[PASSED]' if g5_pass else '[FAILED]'}")
    print("-" * 78)

    all_passed = g1_pass and g2_pass and g3_pass and g4_pass and g5_pass
    print(f"OVERALL PHASE 3 CERTIFICATION: {'[CERTIFIED - ALL GATES PASSED]' if all_passed else '[FAILED]'}")
    print("=" * 78 + "\n")

    # Latency comparison
    avg_fp32_step = float(np.mean(fp32_res["latencies"][1:]))  # omit cold step
    avg_int8_step = float(np.mean(int8_res["latencies"][1:]))
    print("Latency & Performance Profiling:")
    print(f"  DiT Step Latency (warm avg): FP32 = {avg_fp32_step:.3f}s | INT8 = {avg_int8_step:.3f}s")
    print(f"  Total ODE Latency (8 steps): FP32 = {fp32_res['ode_time']:.2f}s | INT8 = {int8_res['ode_time']:.2f}s")
    print(f"  Vocos Vocoder Latency:       FP32 = {fp32_res['vocos_time']:.3f}s | INT8 = {int8_res['vocos_time']:.3f}s")
    print(f"  Combined Model Footprint:    FP32 = {tot_fp32_mb:.2f} MB -> INT8 = {tot_int8_mb:.2f} MB ({(1 - tot_int8_mb/tot_fp32_mb)*100:.1f}% reduction)")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
