#!/usr/bin/env python3
"""
scratch/generate_phrase.py: Synthesize any target phrase using indicf5_dit_int8.tflite.
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

REPO_ROOT = Path("/mnt/c/voice_cloning")
sys.path.insert(0, str(REPO_ROOT))

from ai_edge_litert.interpreter import Interpreter
from vocos import Vocos
from scripts.infer_litert import load_vocab, extract_mel_spectrogram

DIT_INT8_PATH = REPO_ROOT / "models" / "indicf5" / "indicf5_dit_int8.tflite"
VOCAB_PATH = REPO_ROOT / "models" / "indicf5" / "vocab.txt"
REF_AUDIO_PATH = REPO_ROOT / "scratch" / "parity_test" / "trimmed_ref_en.wav"
REF_TEXT = "Some call me nature."


def synthesize(
    gen_text: str,
    output_wav_path: Path,
    steps: int = 24,
    cfg_strength: float = 2.0,
    sway_coef: float = -1.0,
    seed: int = 42,
):
    print("=" * 70)
    print(f"Synthesizing: \"{gen_text}\"")
    print(f"Output File:  {output_wav_path}")
    print(f"ODE Steps:    {steps} | CFG: {cfg_strength} | Seed: {seed}")
    print("=" * 70)

    # 1. Load Vocab & Models
    vocab_char_map = load_vocab(VOCAB_PATH)

    print(f"Loading DiT INT8: {DIT_INT8_PATH.name} ({os.path.getsize(DIT_INT8_PATH)/(1024*1024):.2f} MB)...")
    dit_interp = Interpreter(model_path=str(DIT_INT8_PATH))
    dit_interp.allocate_tensors()
    dit_in = dit_interp.get_input_details()
    dit_out = dit_interp.get_output_details()

    print("Loading Vocos vocoder...")
    vocoder = Vocos.from_pretrained("charactr/vocos-mel-24khz")

    # 2. Extract Reference Mel
    ref_mel_spec, _ = extract_mel_spectrogram(REF_AUDIO_PATH)
    ref_mel = ref_mel_spec.T  # [T_ref, 100]
    ref_audio_len = ref_mel.shape[0]

    # Calculate duration
    ref_char_len = len(REF_TEXT.strip())
    gen_char_len = len(gen_text.strip())
    gen_frames = int(ref_audio_len / ref_char_len * gen_char_len)
    total_duration = min(ref_audio_len + gen_frames, 512)

    print(f"Reference Audio: {ref_audio_len} frames ({ref_audio_len * 256 / 24000:.2f}s) -> '{REF_TEXT}'")
    print(f"Target Speech:   {gen_frames} frames ({gen_frames * 256 / 24000:.2f}s) -> '{gen_text}'")
    print(f"Total Window:    {total_duration} / 512 frames")

    # 3. Prepare Text & Conditioning
    full_text = f"{REF_TEXT.strip()} {gen_text.strip()}"
    tokens = [vocab_char_map.get(c, -1) for c in full_text]
    tokens = tokens[:128] + [-1] * max(0, 128 - len(tokens))
    text_cond = np.array([tokens], dtype=np.int32)
    null_tokens = np.full((1, 128), -1, dtype=np.int32)

    cond_mel = np.zeros((1, 512, 100), dtype=np.float32)
    cond_mel[0, :ref_audio_len, :] = ref_mel.numpy()
    null_cond = np.zeros((1, 512, 100), dtype=np.float32)

    # 4. Sway Sampling Euler ODE
    torch.manual_seed(seed)
    np.random.seed(seed)
    x = np.random.randn(1, 512, 100).astype(np.float32)

    t_steps = torch.linspace(0, 1, steps + 1)
    t_steps = t_steps + sway_coef * (torch.cos(torch.pi / 2 * t_steps) - 1 + t_steps)

    t0 = time.time()
    for i in range(steps):
        t_val = np.array([float(t_steps[i])], dtype=np.float32)
        dt = float(t_steps[i + 1] - t_steps[i])

        # Conditioned pass
        dit_interp.set_tensor(dit_in[0]["index"], x)
        dit_interp.set_tensor(dit_in[1]["index"], cond_mel)
        dit_interp.set_tensor(dit_in[2]["index"], text_cond)
        dit_interp.set_tensor(dit_in[3]["index"], t_val)
        dit_interp.invoke()
        v_cond = dit_interp.get_tensor(dit_out[0]["index"]).copy()

        # Unconditioned pass
        dit_interp.set_tensor(dit_in[0]["index"], x)
        dit_interp.set_tensor(dit_in[1]["index"], null_cond)
        dit_interp.set_tensor(dit_in[2]["index"], null_tokens)
        dit_interp.set_tensor(dit_in[3]["index"], t_val)
        dit_interp.invoke()
        v_null = dit_interp.get_tensor(dit_out[0]["index"]).copy()

        v_pred = v_cond + (v_cond - v_null) * cfg_strength
        x = x + dt * v_pred

    ode_time = time.time() - t0
    print(f"ODE completed in {ode_time:.2f}s ({ode_time / steps / 2:.3f}s / forward pass)")

    # 5. Decode with Vocos
    x[0, :ref_audio_len, :] = cond_mel[0, :ref_audio_len, :]
    gen_mel = x[:, ref_audio_len:total_duration, :]
    gen_mel_torch = torch.from_numpy(gen_mel).permute(0, 2, 1).float()

    with torch.inference_mode():
        gen_wav = vocoder.decode(gen_mel_torch).squeeze().cpu().numpy()

    # Peak normalize
    max_val = np.max(np.abs(gen_wav))
    if max_val > 1e-4:
        gen_wav = gen_wav * (0.95 / max_val)

    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_wav_path), gen_wav, 24000)
    dur = len(gen_wav) / 24000.0
    print(f"[SUCCESS] Saved {dur:.2f}s speech to: {output_wav_path}\n")
    return output_wav_path, dur


def main():
    parser = argparse.ArgumentParser(description="Generate voice cloned speech using DiT INT8")
    parser.add_argument("--text", type=str, required=True, help="Text phrase to synthesize")
    parser.add_argument("--out", type=str, required=True, help="Output .wav path")
    parser.add_argument("--steps", type=int, default=24, help="ODE steps (default: 24)")
    parser.add_argument("--cfg", type=float, default=2.0, help="CFG strength (default: 2.0)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    synthesize(
        gen_text=args.text,
        output_wav_path=Path(args.out),
        steps=args.steps,
        cfg_strength=args.cfg,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
