#!/usr/bin/env python3
"""
Indic Voice Studio — English Zero-Shot Voice Cloning & TTS Tool
Powered by Sherpa-ONNX ZipVoice-Distill INT8 ONNX and Vocos.

Usage:
    python english_tts.py `
      --ref "samples/vamsi.ogg" `
      --ref-text "The quick brown fox jumps over the lazy dog..." `
      --text "Hello everyone, welcome to the on-device voice cloning pipeline." `
      --format mp3
"""

import sys
import argparse
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from voice_studio.engines.zipvoice import ZipVoiceEngine
from voice_studio.catalog.manager import VoiceCatalog


def main():
    parser = argparse.ArgumentParser(
        description="Sherpa-ONNX ZipVoice English Zero-Shot Voice Cloning Tool",
    )
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default="",
        help="Preset voice key from voices.json (e.g. sudhanva_english)",
    )
    parser.add_argument(
        "--ref", "-r",
        type=str,
        default="samples/vamsi.ogg",
        help="Path to reference audio file",
    )
    parser.add_argument(
        "--ref-text",
        type=str,
        default="The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley.",
        help="Spoken transcript of the reference audio",
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        default="Hello everyone, this is a test of zero-shot neural voice cloning running locally on device.",
        help="Target English text to synthesize",
    )
    parser.add_argument(
        "--out", "-o",
        type=str,
        default="",
        help="Output audio path (default: generated/<ref>_zipvoice_<ts>.<format>)",
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        default="wav",
        choices=["wav", "mp3", "ogg", "flac"],
        help="Output container format (default: wav)",
    )
    parser.add_argument(
        "--steps", "-s",
        type=int,
        default=4,
        help="Synthesis diffusion steps (default: 4)",
    )
    args = parser.parse_args()

    ref_audio = args.ref
    ref_text = args.ref_text

    if args.voice:
        catalog = VoiceCatalog()
        v = catalog.get_voice(args.voice)
        if v and v["audio_exists"]:
            ref_audio = v["resolved_audio_path"]
            ref_text = v.get("transcript", "")
            print(f"[Preset Voice] Loaded voice '{args.voice}'")
        else:
            print(f"[Error] Voice key '{args.voice}' not found or audio file missing.")
            return

    engine = ZipVoiceEngine()
    print("=" * 70)
    print(" Sherpa-ONNX ZipVoice English Voice Cloning")
    print("=" * 70)
    print(f" Reference Audio : {ref_audio}")
    print(f" Target Text     : {args.text}")
    print("-" * 70)

    res = engine.generate(
        text=args.text,
        reference_audio_path=ref_audio,
        reference_text=ref_text,
        output_path=args.out if args.out else None,
        audio_format=args.format,
        num_steps=args.steps,
    )

    print("=" * 70)
    print(f" ✓ Synthesis Complete: {res['output_path']}")
    print(f"  Duration: {res['duration_sec']:.2f}s | Gen Time: {res['elapsed_sec']:.3f}s | RTF: {res['rtf']:.3f}x")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
