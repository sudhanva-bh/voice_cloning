#!/usr/bin/env python3
"""
IndicF5 High-Fidelity Zero-Shot Voice Cloning CLI Test
Supports Tamil, Hindi, Telugu, Kannada, Malayalam, Marathi, Gujarati, Bengali, Punjabi, Odia, Assamese.

Usage:
    .\\sherpa-env\\Scripts\\python.exe test_indicf5_clone.py `
      --ref "samples/sudhanva_voic_clone.wav" `
      --ref-text "The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley." `
      --text "ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಾ? ನಾನು ಈಗ ನಿಮ್ಮ ಧ್ವನಿಯಲ್ಲಿ ಕನ್ನಡ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ." `
      --out "generated/sudhanva_kannada_fixed.wav"
"""

import sys
import codecs
import time
import argparse
from pathlib import Path

# Add repo path
sys.path.insert(0, str(Path("scratch/indicf5_repo").resolve()))

# UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

import torch
import librosa
import soundfile as sf
from safetensors.torch import load_file
from f5_tts.model.cfm import CFM
from f5_tts.model.backbones.dit import DiT
from f5_tts.model.utils import get_tokenizer
from vocos import Vocos

# Constants
MODEL_DIR = Path("models/indicf5")
SAFETENSORS_PATH = MODEL_DIR / "model.safetensors"
VOCAB_PATH = MODEL_DIR / "vocab.txt"
SAMPLE_RATE = 24000
HOP_LENGTH = 256


def clone_voice(
    reference_audio_path: str,
    target_text: str,
    reference_text: str,
    output_wav_path: str = "generated/indicf5_cloned.wav",
    num_steps: int = 16,
    cfg_strength: float = 2.0,
    speed: float = 1.0,
    extra_duration_sec: float = 0.5,
):
    print("=" * 70)
    print(" IndicF5 High-Fidelity Zero-Shot Voice Cloning")
    print("=" * 70)
    print(f"Reference Audio  : {reference_audio_path}")
    print(f"Reference Text   : {reference_text}")
    print(f"Target Text      : {target_text}")
    print(f"Diffusion Steps   : {num_steps} (CFG: {cfg_strength})")
    print("-" * 70)

    # 1. Load Tokenizer & Vocab
    vocab_map, vocab_size = get_tokenizer(str(VOCAB_PATH), "custom")

    # 2. Build CFM & DiT
    transformer = DiT(
        dim=1024,
        depth=22,
        heads=16,
        dim_head=64,
        ff_mult=2,
        text_dim=512,
        conv_layers=4,
        text_num_embeds=vocab_size,
        mel_dim=100,
    )

    model = CFM(
        transformer=transformer,
        mel_spec_kwargs=dict(
            n_fft=1024,
            hop_length=256,
            win_length=1024,
            n_mel_channels=100,
            target_sample_rate=SAMPLE_RATE,
            mel_spec_type="vocos",
        ),
        odeint_kwargs=dict(method="euler"),
        vocab_char_map=vocab_map,
    )

    # 3. Load Weights
    print("[1/3] Loading IndicF5 Safetensors model...")
    weights = load_file(str(SAFETENSORS_PATH))
    clean_weights = {}
    for k, v in weights.items():
        if k.startswith("transformer."):
            clean_weights[k] = v
        elif k.startswith("ema_model.transformer."):
            clean_weights[k.replace("ema_model.transformer.", "transformer.")] = v
        else:
            clean_weights[k] = v

    model.load_state_dict(clean_weights, strict=False)
    model = model.eval()

    # 4. Load Vocoder
    vocoder = Vocos.from_pretrained("charactr/vocos-mel-24khz").eval()

    # 5. Load Reference Audio (Full audio matching the full reference text)
    y, sr = librosa.load(reference_audio_path, sr=SAMPLE_RATE, mono=True)
    audio = torch.from_numpy(y).unsqueeze(0).float()

    ref_audio_len = audio.shape[-1] // HOP_LENGTH

    # Calculate generation duration accurately for Indic script
    # Indic characters are syllabic (aksharas) and take ~14 to 18 mel frames per character
    # English reference text is alphabetic (~6 to 8 frames per character)
    # We use a robust duration estimation with safety padding
    indic_frames_per_char = 15.0 / speed
    gen_frames = int(len(target_text.strip()) * indic_frames_per_char)
    extra_pad_frames = int(extra_duration_sec * SAMPLE_RATE / HOP_LENGTH)
    
    # Total duration = full reference audio + generated frames + buffer
    duration = ref_audio_len + gen_frames + extra_pad_frames

    print(f"Reference duration : {ref_audio_len * HOP_LENGTH / SAMPLE_RATE:.2f} s ({ref_audio_len} frames)")
    print(f"Target duration    : {(duration - ref_audio_len) * HOP_LENGTH / SAMPLE_RATE:.2f} s ({duration - ref_audio_len} frames)")
    print(f"Total window       : {duration * HOP_LENGTH / SAMPLE_RATE:.2f} s ({duration} frames)")

    # Ensure punctuation boundary between reference text and target text
    clean_ref_text = reference_text.strip()
    if not clean_ref_text.endswith((".", "!", "?", "।")):
        clean_ref_text += "."
    
    text_list = [clean_ref_text + " " + target_text.strip()]

    # 6. Run Flow-Matching Diffusion
    print(f"\n[2/3] Running Flow-Matching Diffusion ({num_steps} Euler steps with CFG {cfg_strength})...")
    start_time = time.time()

    with torch.inference_mode():
        generated, _ = model.sample(
            cond=audio,
            text=text_list,
            duration=duration,
            steps=num_steps,
            cfg_strength=cfg_strength,
            sway_sampling_coef=-1.0,
        )
        generated = generated.to(torch.float32)
        # Extract only the generated portion (after reference audio)
        generated = generated[:, ref_audio_len:, :]
        generated_mel_spec = generated.permute(0, 2, 1)

        print("[3/3] Decoding with Vocos neural vocoder...")
        generated_wave = vocoder.decode(generated_mel_spec)
        wav = generated_wave.squeeze().cpu().numpy()

    elapsed = time.time() - start_time
    duration_sec = len(wav) / SAMPLE_RATE

    # 7. Save output
    out_path = Path(output_wav_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_path), wav, samplerate=SAMPLE_RATE, subtype="PCM_16")

    print("\n" + "=" * 70)
    print(f" SUCCESS! Cloned audio saved to: {out_path.resolve()}")
    print(f" Audio Duration : {duration_sec:.2f} seconds")
    print(f" Generation Time: {elapsed:.2f} seconds")
    print(f" RTF (Speed)    : {elapsed / duration_sec:.2f}x")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IndicF5 Voice Cloning CLI Test")
    parser.add_argument(
        "--ref",
        type=str,
        default="samples/sudhanva_voic_clone.wav",
        help="Path to reference audio file",
    )
    parser.add_argument(
        "--ref-text",
        type=str,
        default="The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley.",
        help="Transcript of the reference audio",
    )
    parser.add_argument(
        "--text",
        type=str,
        default="ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಾ? ನಾನು ಈಗ ನಿಮ್ಮ ಧ್ವನಿಯಲ್ಲಿ ಕನ್ನಡ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ.",
        help="Target text in Tamil, Hindi, Kannada, Telugu, etc.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="generated/sudhanva_kannada_fixed.wav",
        help="Output audio path",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=16,
        help="Diffusion steps (default: 16)",
    )
    parser.add_argument(
        "--cfg",
        type=float,
        default=2.0,
        help="Classifier-Free Guidance strength (default: 2.0)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed multiplier (default: 1.0)",
    )
    args = parser.parse_args()

    clone_voice(
        reference_audio_path=args.ref,
        target_text=args.text,
        reference_text=args.ref_text,
        output_wav_path=args.out,
        num_steps=args.steps,
        cfg_strength=args.cfg,
        speed=args.speed,
    )
