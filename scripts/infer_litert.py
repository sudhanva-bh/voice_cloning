#!/usr/bin/env python3
"""
End-to-End On-Device Voice Cloning Inference Harness with Google LiteRT.
Executes the Continuous Flow Matching (CFM) Euler ODE diffusion loop using
indicf5_dit_fp32.tflite and synthesizes audio using indicf5_vocos_fp32.tflite.
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

# Try importing LiteRT interpreter
try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    try:
        from litert.interpreter import Interpreter
    except ImportError:
        from tflite_runtime.interpreter import Interpreter

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIT = REPO_ROOT / "models" / "indicf5" / "indicf5_dit_fp32.tflite"
DEFAULT_VOCOS = REPO_ROOT / "models" / "indicf5" / "indicf5_vocos_fp32.tflite"
DEFAULT_VOCAB = REPO_ROOT / "models" / "indicf5" / "vocab.txt"


def load_vocab(vocab_file: Path) -> dict[str, int]:
    """Loads char/token map from vocab.txt."""
    vocab_map = {}
    with open(vocab_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            vocab_map[line.rstrip("\r\n")] = idx
    return vocab_map


def text_to_tokens(text: str, vocab_map: dict[str, int], max_len: int = 128) -> np.ndarray:
    """Converts input text string to token ID array padded to max_len."""
    tokens = [vocab_map.get(ch, 0) for ch in text]
    tokens = tokens[:max_len]
    pad_len = max_len - len(tokens)
    if pad_len > 0:
        tokens = tokens + [0] * pad_len
    return np.array([tokens], dtype=np.int32)


def extract_mel_spectrogram(
    audio_path: Path,
    target_sample_rate: int = 24000,
    hop_length: int = 256,
    win_length: int = 1024,
    n_fft: int = 1024,
    n_mels: int = 100,
    target_rms: float = 0.1,
) -> tuple[torch.Tensor, float]:
    """Loads, resamples, RMS-normalizes audio and extracts mel spectrogram."""
    wav_np, sr = sf.read(str(audio_path))
    wav = torch.from_numpy(wav_np).float()
    if wav.ndim == 1:
        wav = wav.unsqueeze(0)
    elif wav.ndim == 2:
        wav = wav.T  # [channels, samples]

    rms = torch.sqrt(torch.mean(torch.square(wav)))
    if rms < target_rms and rms > 1e-6:
        wav = wav * (target_rms / rms)

    if sr != target_sample_rate:
        resampler = torchaudio.transforms.Resample(sr, target_sample_rate)
        wav = resampler(wav)

    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=target_sample_rate,
        n_fft=n_fft,
        win_length=win_length,
        hop_length=hop_length,
        n_mels=n_mels,
        power=1,
        center=True,
        normalized=False,
        norm=None,
    )
    mel = mel_transform(wav)
    mel = mel.clamp(min=1e-5).log()
    return mel.squeeze(0), float(rms)


def synthesize_audio_from_spec(
    real: torch.Tensor,
    imag: torch.Tensor,
    n_fft: int = 1024,
    hop_length: int = 256,
    win_length: int = 1024,
) -> np.ndarray:
    """Performs windowed overlap-add iSTFT synthesis from real and imaginary spectra."""
    complex_spec = torch.complex(real, imag)
    window = torch.hann_window(win_length, device=complex_spec.device)
    wav = torch.istft(
        complex_spec,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        window=window,
        center=True,
    )
    return wav.squeeze().cpu().numpy()


def generate_speech_litert(
    ref_audio_path: Path,
    ref_text: str,
    gen_text: str,
    dit_model_path: Path = DEFAULT_DIT,
    vocos_model_path: Path = DEFAULT_VOCOS,
    vocab_path: Path = DEFAULT_VOCAB,
    output_path: Path = None,
    steps: int = 8,
    seed: int = 42,
    seq_bucket: int = 512,
    text_len: int = 128,
) -> tuple[np.ndarray, float]:
    """
    Executes end-to-end voice cloning inference with Google LiteRT.
    Returns: (synthesized_waveform, total_latency_seconds)
    """
    t_start = time.time()

    print("=" * 78)
    print("      GOOGLE LITERt VOICE CLONING INFERENCE — CONTINUOUS FLOW MATCHING")
    print("=" * 78)
    print(f"Reference Audio: {ref_audio_path}")
    print(f"Reference Text:  \"{ref_text}\"")
    print(f"Target Text:     \"{gen_text}\"")
    print(f"DiT Model:       {dit_model_path.name}")
    print(f"Vocos Model:     {vocos_model_path.name}")
    print(f"ODE Steps:       {steps}")

    # 1. Feature Extraction & Preprocessing
    print("\n[Step 1/4] Preprocessing audio and tokenizing text...")
    ref_mel, ref_rms = extract_mel_spectrogram(ref_audio_path)
    ref_frames = ref_mel.shape[-1]

    # Cap reference audio to half the bucket (e.g. 256 frames ~ 2.7 sec)
    # to guarantee at least 256 frames of headroom for target speech generation
    max_ref_frames = seq_bucket // 2
    if ref_frames > max_ref_frames:
        print(f"  Reference audio has {ref_frames} frames. Slicing to {max_ref_frames} frames (~{max_ref_frames * 256 / 24000:.2f}s) for bucket balance.")
        ref_mel = ref_mel[:, :max_ref_frames]
        ref_frames = max_ref_frames

    # Calculate target length proportionally
    ref_char_len = max(len(ref_text), 1)
    gen_char_len = max(len(gen_text), 1)
    gen_frames = int(ref_frames / ref_char_len * gen_char_len)
    total_frames = min(ref_frames + gen_frames, seq_bucket)
    print(f"  Reference Mel: {ref_frames} frames | Estimated Target: {gen_frames} frames | Total: {total_frames} frames")

    # Vocab and Tokenization
    vocab_map = load_vocab(vocab_path)
    full_text = f"{ref_text.strip()} {gen_text.strip()}"
    tokens = text_to_tokens(full_text, vocab_map, max_len=text_len)

    # Prepare input tensors
    cond_mel = np.zeros((1, seq_bucket, 100), dtype=np.float32)
    # Transpose [100, ref_frames] -> [ref_frames, 100]
    ref_mel_np = ref_mel.numpy().T
    actual_ref_len = min(ref_frames, seq_bucket)
    cond_mel[0, :actual_ref_len, :] = ref_mel_np[:actual_ref_len, :]

    # Initial Gaussian Noise
    np.random.seed(seed)
    x = np.random.randn(1, seq_bucket, 100).astype(np.float32)

    # 2. Initialize LiteRT Interpreters
    print("\n[Step 2/4] Initializing LiteRT XNNPACK Interpreters...")
    dit_interp = Interpreter(model_path=str(dit_model_path))
    dit_interp.allocate_tensors()
    dit_in = dit_interp.get_input_details()
    dit_out = dit_interp.get_output_details()

    vocos_interp = Interpreter(model_path=str(vocos_model_path))
    vocos_interp.allocate_tensors()
    vocos_in = vocos_interp.get_input_details()
    vocos_out = vocos_interp.get_output_details()

    # 3. Continuous Flow Matching (CFM) Euler ODE Loop
    print(f"\n[Step 3/4] Solving Continuous Flow Matching ODE ({steps} Euler steps)...")
    dt = 1.0 / steps
    t_ode_start = time.time()

    for step in range(steps):
        t_val = np.array([step / float(steps)], dtype=np.float32)

        # Bind inputs to DiT: [x, cond, text, time]
        dit_interp.set_tensor(dit_in[0]["index"], x)
        dit_interp.set_tensor(dit_in[1]["index"], cond_mel)
        dit_interp.set_tensor(dit_in[2]["index"], tokens)
        dit_interp.set_tensor(dit_in[3]["index"], t_val)

        t_step0 = time.time()
        dit_interp.invoke()
        step_latency = time.time() - t_step0

        v_pred = dit_interp.get_tensor(dit_out[0]["index"])
        # Euler update: x_{i+1} = x_i + dt * v_t
        x = x + dt * v_pred

        print(f"  Step [{step + 1}/{steps}] (t={t_val[0]:.3f}): Latency {step_latency:.3f}s | Velocity L2: {np.linalg.norm(v_pred):.2f}")

    ode_total_time = time.time() - t_ode_start
    print(f"  [PASSED] ODE Diffusion completed in {ode_total_time:.2f}s ({ode_total_time / steps:.3f}s/step)")

    # Restore reference audio portion in mel
    x[0, :actual_ref_len, :] = cond_mel[0, :actual_ref_len, :]

    # 4. Neural Vocoding with LiteRT Vocos
    print("\n[Step 4/4] Synthesizing 24 kHz audio with LiteRT Vocos...")
    # Transpose [1, 512, 100] -> [1, 100, 512] for Vocos
    mel_for_vocos = np.transpose(x, (0, 2, 1))

    vocos_interp.set_tensor(vocos_in[0]["index"], mel_for_vocos)
    t_voc0 = time.time()
    vocos_interp.invoke()
    vocos_time = time.time() - t_voc0

    # Output: [1, 2, 513, 512]
    complex_spec = vocos_interp.get_tensor(vocos_out[0]["index"])
    real_part = torch.from_numpy(complex_spec[0, 0, :, :])
    imag_part = torch.from_numpy(complex_spec[0, 1, :, :])

    # Windowed overlap-add iSTFT
    full_wav = synthesize_audio_from_spec(real_part, imag_part)

    # Slice target audio (excluding reference audio portion)
    start_sample = actual_ref_len * 256
    end_sample = total_frames * 256
    gen_wav = full_wav[start_sample:end_sample]

    # Peak normalization
    max_val = np.max(np.abs(gen_wav))
    if max_val > 1e-4:
        gen_wav = gen_wav * (0.95 / max_val)

    total_latency = time.time() - t_start
    audio_dur = len(gen_wav) / 24000.0
    rtf = total_latency / max(audio_dur, 1e-4)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(output_path), gen_wav, 24000)
        print(f"  [PASSED] Saved generated voice to: {output_path}")

    print("\n" + "=" * 78)
    print("                     INFERENCE PERFORMANCE SUMMARY")
    print("=" * 78)
    print(f"  Generated Speech Duration:  {audio_dur:.2f} seconds ({len(gen_wav)} samples)")
    print(f"  Total End-to-End Latency:   {total_latency:.2f} seconds")
    print(f"  ODE Diffusion Latency:      {ode_total_time:.2f} seconds")
    print(f"  Vocos Vocoder Latency:      {vocos_time:.3f} seconds")
    print(f"  Real-Time Factor (RTF):     {rtf:.3f}x ({'FASTER THAN REALTIME' if rtf <= 1.0 else 'SLOWER THAN REALTIME'})")
    print("=" * 78 + "\n")

    return gen_wav, total_latency


def main():
    parser = argparse.ArgumentParser(description="End-to-End LiteRT Voice Cloning Inference")
    parser.add_argument("--ref_audio", type=str, required=True, help="Path to reference audio file (.wav)")
    parser.add_argument("--ref_text", type=str, required=True, help="Transcript of reference audio")
    parser.add_argument("--gen_text", type=str, required=True, help="Target text to clone and synthesize")
    parser.add_argument("--dit_model", type=str, default=str(DEFAULT_DIT), help="Path to indicf5_dit_fp32.tflite")
    parser.add_argument("--vocos_model", type=str, default=str(DEFAULT_VOCOS), help="Path to indicf5_vocos_fp32.tflite")
    parser.add_argument("--vocab", type=str, default=str(DEFAULT_VOCAB), help="Path to vocab.txt")
    parser.add_argument("--output", type=str, default="scratch/parity_test/litert_fp32.wav", help="Output .wav path")
    parser.add_argument("--steps", type=int, default=8, help="Number of Euler ODE steps (default: 8)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for Gaussian noise")

    args = parser.parse_args()
    generate_speech_litert(
        ref_audio_path=Path(args.ref_audio),
        ref_text=args.ref_text,
        gen_text=args.gen_text,
        dit_model_path=Path(args.dit_model),
        vocos_model_path=Path(args.vocos_model),
        vocab_path=Path(args.vocab),
        output_path=Path(args.output),
        steps=args.steps,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
