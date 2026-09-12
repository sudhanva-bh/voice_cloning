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

# Force unbuffered UTF-8 stdout and stderr for instant real-time printing
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True, write_through=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True, write_through=True)
    except AttributeError:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Override built-in print to ALWAYS flush immediately
_orig_print = print
def print(*args, **kwargs):
    kwargs.setdefault("flush", True)
    _orig_print(*args, **kwargs)

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


def save_audio(out_path: str, wav, sample_rate: int = SAMPLE_RATE, fmt: str = "wav") -> Path:
    path = Path(out_path)
    # If explicit format given and doesn't match extension, adjust suffix
    if fmt and fmt.lower() in ("wav", "mp3", "ogg", "flac"):
        if path.suffix.lower().replace(".", "") != fmt.lower():
            path = path.with_suffix(f".{fmt.lower()}")
    
    ext = path.suffix.lower().replace(".", "")
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if ext == "mp3":
        sf.write(str(path), wav, samplerate=sample_rate, format="MP3")
    elif ext in ("ogg", "oga"):
        sf.write(str(path), wav, samplerate=sample_rate, format="OGG")
    elif ext == "flac":
        sf.write(str(path), wav, samplerate=sample_rate, format="FLAC")
    else:
        sf.write(str(path), wav, samplerate=sample_rate, subtype="PCM_16")
    return path


def clone_voice(
    reference_audio_path: str,
    target_text: str,
    reference_text: str,
    output_wav_path: str = "generated/indicf5_cloned.wav",
    audio_format: str = "wav",
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

    # Normalize audio RMS to standard 0.1 level
    target_rms = 0.1
    rms = torch.sqrt(torch.mean(torch.square(audio)))
    if rms < target_rms and rms.item() > 1e-6:
        audio = audio * (target_rms / rms.item())

    ref_audio_len = audio.shape[-1] // HOP_LENGTH

    # Calculate generation duration accurately for Indic script
    # In Indic Unicode strings (including aksharas, matras, viramas), each code point averages ~5.5 to 7.0 mel frames (~60ms).
    # Previous 15.0 frames/char caused 2.5x overestimation, creating huge gaps of silence and babbling.
    indic_frames_per_char = 6.5 / speed
    gen_frames = int(len(target_text.strip()) * indic_frames_per_char)
    extra_pad_frames = int(extra_duration_sec * SAMPLE_RATE / HOP_LENGTH)

    # Total duration = full reference audio + generated frames + buffer
    duration = ref_audio_len + gen_frames + extra_pad_frames

    print(
        f"Reference duration : {ref_audio_len * HOP_LENGTH / SAMPLE_RATE:.2f} s ({ref_audio_len} frames)"
    )
    print(
        f"Target duration    : {(duration - ref_audio_len) * HOP_LENGTH / SAMPLE_RATE:.2f} s ({duration - ref_audio_len} frames)"
    )
    print(
        f"Total window       : {duration * HOP_LENGTH / SAMPLE_RATE:.2f} s ({duration} frames)"
    )

    # Ensure punctuation boundary between reference text and target text
    clean_ref_text = reference_text.strip()
    if not clean_ref_text.endswith((".", "!", "?", "।")):
        clean_ref_text += "."

    text_list = [clean_ref_text + " " + target_text.strip()]

    # 6. Run Flow-Matching Diffusion
    print(
        f"\n[2/3] Running Flow-Matching Diffusion ({num_steps} Euler steps with CFG {cfg_strength})..."
    )
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
    saved_path = save_audio(output_wav_path, wav, sample_rate=SAMPLE_RATE, fmt=audio_format)

    print("\n" + "=" * 70)
    print(f" SUCCESS! Cloned audio saved to: {saved_path.resolve()} [{saved_path.suffix.upper()}]")
    print(f" Audio Duration : {duration_sec:.2f} seconds")
    print(f" Generation Time: {elapsed:.2f} seconds")
    print(f" RTF (Speed)    : {elapsed / duration_sec:.2f}x")
    print("=" * 70)


import json


def load_voice_from_json(voice_key: str, json_path: str = "samples/voices.json"):
    path = Path(json_path)
    if not path.is_file():
        # Fallback check
        alt_json = Path("samples/tamil_voices/voices.json")
        if alt_json.is_file():
            path = alt_json
        else:
            raise FileNotFoundError(f"Voices JSON mapping file not found at: {json_path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if voice_key not in data:
        available = "\n  - " + "\n  - ".join(data.keys())
        raise KeyError(f"Voice key '{voice_key}' not found in {path}. Available keys:{available}")
    entry = data[voice_key]
    audio_path = entry["audio"]
    
    # Resolve audio path robustly
    audio_p = Path(audio_path)
    if not audio_p.is_file():
        candidates = [
            path.parent / audio_path,
            path.parent / audio_p.name,
            Path("samples") / audio_path,
            Path("samples/added") / audio_p.name,
            Path("samples/tamil_voices") / audio_p.name,
        ]
        for c in candidates:
            if c.is_file():
                audio_path = str(c)
                break
    return audio_path, entry["transcript"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IndicF5 Voice Cloning CLI Test")
    parser.add_argument(
        "--voice",
        "--voice-key",
        type=str,
        default=None,
        help="Preset voice key from voices.json (e.g. tamil_classic_pangram, deep_classic, sudhanva_english)",
    )
    parser.add_argument(
        "--voices-json",
        type=str,
        default="samples/voices.json",
        help="Path to voices.json mapping file (default: samples/voices.json)",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available preset voice keys from voices.json and exit",
    )
    parser.add_argument(
        "--ref",
        type=str,
        default="samples/sudhanva_short_ref.wav",
        help="Path to reference audio file",
    )
    parser.add_argument(
        "--ref-text",
        type=str,
        default="The quick brown fox jumps over the lazy dog.",
        help="Transcript of the reference audio",
    )
    parser.add_argument(
        "--text",
        type=str,
        default="నమస్కారం, మీరు ఎలా ఉన్నారు? నేను ఇప్పుడు మీ గొంతుతో తెలుగు మాట్లాడుతున్నాను.",
        help="Target text in Tamil, Hindi, Kannada, Telugu, etc.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="generated/kannada_fixed.wav",
        help="Output audio path",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        default="wav",
        choices=["wav", "mp3", "ogg", "flac"],
        help="Output audio format: wav, mp3, ogg, or flac (default: wav)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=8,
        help="Diffusion steps (default: 8)",
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
    parser.add_argument(
        "--extra-pad",
        type=float,
        default=0.3,
        help="Extra safety duration padding in seconds (default: 0.3)",
    )
    args = parser.parse_args()

    # If listing voices, display available keys and exit
    if args.list_voices:
        json_path = Path(args.voices_json)
        if not json_path.is_file():
            print(f"Voices JSON file not found at: {json_path}")
            sys.exit(1)
        with open(json_path, "r", encoding="utf-8") as f:
            voices = json.load(f)
        print("=" * 70)
        print(f" Available Voice Keys in {json_path.resolve()}")
        print("=" * 70)
        for key, info in voices.items():
            print(f" Key   : {key}")
            print(f" Audio : {info.get('audio')}")
            print(f" Desc  : {info.get('description', '')}")
            print(f" Text  : {info.get('transcript')}")
            print("-" * 70)
        sys.exit(0)

    ref_audio = args.ref
    ref_text = args.ref_text

    # Resolve from voices.json if voice key is specified
    if args.voice:
        ref_audio, ref_text = load_voice_from_json(args.voice, args.voices_json)
        print(f"[Preset Voice] Loaded voice '{args.voice}' from {args.voices_json}")

    clone_voice(
        reference_audio_path=ref_audio,
        target_text=args.text,
        reference_text=ref_text,
        output_wav_path=args.out,
        audio_format=args.format,
        num_steps=args.steps,
        cfg_strength=args.cfg,
        speed=args.speed,
        extra_duration_sec=args.extra_pad,
    )
