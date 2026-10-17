#!/usr/bin/env python3
"""
cli/synthesize.py: Clean Command-Line Interface for Google LiteRT Indic Voice Cloning.

Usage:
    python cli/synthesize.py --text "Your sentence here" --out "output.wav" [options]
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from voice_studio.engines.litert_indic import (
    LiteRTIndicEngine,
    DEFAULT_DIT_INT8,
    DEFAULT_VOCOS_INT8,
)
from voice_studio.config import VOCAB_PATH

DEFAULT_REF_AUDIO = REPO_ROOT / "scratch" / "parity_test" / "trimmed_ref_en.wav"
DEFAULT_REF_TEXT = "Some call me nature."


def parse_args():
    parser = argparse.ArgumentParser(
        description="Google LiteRT INT8 On-Device Voice Cloning Synthesizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--text", "-t", type=str, required=True, help="Target text to clone and synthesize")
    parser.add_argument("--out", "-o", type=str, required=True, help="Output destination (.wav)")
    parser.add_argument("--ref_audio", "-r", type=str, default=str(DEFAULT_REF_AUDIO), help="Path to reference audio")
    parser.add_argument("--ref_text", "-s", type=str, default=DEFAULT_REF_TEXT, help="Transcript of reference audio")
    parser.add_argument("--steps", type=int, default=24, help="Euler ODE integration steps (8 to 32)")
    parser.add_argument("--cfg", type=float, default=2.0, help="Classifier-Free Guidance strength")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")
    parser.add_argument("--dit_model", type=str, default=str(DEFAULT_DIT_INT8), help="Path to DiT INT8 model")
    parser.add_argument("--vocos_model", type=str, default=str(DEFAULT_VOCOS_INT8), help="Path to Vocos INT8 model")
    parser.add_argument("--vocab", type=str, default=str(VOCAB_PATH), help="Path to vocab.txt")
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 70)
    print("Google LiteRT Voice Cloning Studio (INT8 Model)")
    print("=" * 70)

    engine = LiteRTIndicEngine(
        dit_path=args.dit_model,
        vocos_path=args.vocos_model,
        vocab_path=args.vocab,
        verbose=True,
    )

    result = engine.synthesize(
        reference_audio_path=args.ref_audio,
        reference_text=args.ref_text,
        target_text=args.text,
        output_wav_path=args.out,
        num_steps=args.steps,
        cfg_strength=args.cfg,
        seed=args.seed,
    )

    print("=" * 70)
    print(f"Synthesized Speech Audio: {result['output_path']}")
    print(f"Speech Duration:          {result['audio_duration_sec']:.2f} seconds")
    print(f"Total Inference Time:     {result['total_elapsed_sec']:.2f} seconds")
    print(f"Real-Time Factor (RTF):   {result['rtf']:.2f}x")
    print("=" * 70)


if __name__ == "__main__":
    main()
