#!/usr/bin/env python3
"""
Indic Voice Studio — Single-Utterance Voice Cloning Tool
High-fidelity zero-shot voice cloning using IndicF5 (Continuous Flow Matching DiT).

Usage:
    # 1. Using a preset voice key from voices.json (Recommended):
    python clone.py --voice deep_classic --text "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?" --format mp3

    # 2. List available voice presets:
    python clone.py --list-voices

    # 3. Using custom reference audio & transcript:
    python clone.py `
      --ref "samples/sudhanva_short_ref.wav" `
      --ref-text "The quick brown fox jumps over the lazy dog." `
      --text "నమస్కారం, మీరు ఎలా ఉన్నారు?" `
      --out "generated/sample.wav"
"""

import sys
import argparse
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from voice_studio.config import VOICES_JSON
from voice_studio.cli.commands import cmd_clone, cmd_list


def main():
    parser = argparse.ArgumentParser(
        description="IndicF5 Single-Utterance Zero-Shot Voice Cloning",
    )
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default="default",
        help="Preset voice key from voices.json (default: 'default', clone of deep_classic)",
    )
    parser.add_argument(
        "--voices-json",
        type=str,
        default=str(VOICES_JSON),
        help="Path to voices.json mapping file (default: samples/voices.json)",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available preset voice keys from voices.json and exit",
    )
    parser.add_argument(
        "--ref", "-r",
        type=str,
        default="samples/sudhanva_short_ref.wav",
        help="Path to reference audio file",
    )
    parser.add_argument(
        "--ref-text",
        type=str,
        default="The quick brown fox jumps over the lazy dog.",
        help="Transcript of reference audio",
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        default="నమస్కారం, మీరు ఎలా ఉన్నారు? నేను ఇప్పుడు మీ గొంతుతో తెలుగు మాట్లాడుతున్నాను.",
        help="Target text in Tamil, Telugu, Hindi, Kannada, etc.",
    )
    parser.add_argument(
        "--out", "-o",
        type=str,
        default="",
        help="Output audio path (default: generated/<key>_cloned.<format>)",
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        default="wav",
        choices=["wav", "mp3", "ogg", "flac"],
        help="Output audio container format (default: wav)",
    )
    parser.add_argument(
        "--steps", "-s",
        type=int,
        default=8,
        help="Euler ODE diffusion steps (default: 8)",
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
    json_path = Path(args.voices_json)

    if args.list_voices:
        cmd_list(json_path)
        return

    cmd_clone(
        voice_key=args.voice if args.voice else "",
        ref_audio=args.ref if not args.voice else "",
        ref_text=args.ref_text if not args.voice else "",
        target_text=args.text,
        out_path=args.out,
        audio_format=args.format,
        steps=args.steps,
        cfg=args.cfg,
        speed=args.speed,
        json_path=json_path,
    )


if __name__ == "__main__":
    main()
