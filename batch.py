#!/usr/bin/env python3
"""
Indic Voice Studio — Batch Voice Cloning & Benchmark Tool
Synthesizes multiple conversational phrases across languages and duration tiers with in-memory model reuse.

Usage:
    # 1. Using a preset voice key with multi-selection:
    python batch.py --voice deep_classic --lang "1 2" --tier "2-4" --count "1-3" --format mp3

    # 2. List available phrases in prompts dataset:
    python batch.py --list-prompts

    # 3. List available voice presets:
    python batch.py --list-voices
"""

import sys
import argparse
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from voice_studio.config import VOICES_JSON, PROMPTS_JSON
from voice_studio.cli.commands import cmd_batch, cmd_list, cmd_prompts


def main():
    parser = argparse.ArgumentParser(
        description="IndicF5 Multilingual Batch Voice Cloning Tool",
    )
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default="deep_classic",
        help="Preset voice key from voices.json (default: deep_classic)",
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
        help="List all available preset voice keys and exit",
    )
    parser.add_argument(
        "--prompts-file",
        type=str,
        default=str(PROMPTS_JSON),
        help="Path to prompts dataset JSON file (default: prompts.json)",
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List all available phrases in dataset and exit",
    )
    parser.add_argument(
        "--lang", "--language",
        type=str,
        default="all",
        help="Language filter: 'all', '1 2' (Telugu+Tamil), '2 3' (Tamil+Hindi), 'telugu,tamil' (default: all)",
    )
    parser.add_argument(
        "--tier", "--length",
        type=str,
        default="all",
        help="Length tier filter: 'all', '1 2', '2-4', 'short,medium' (default: all)",
    )
    parser.add_argument(
        "--count", "--limit",
        type=str,
        default="1",
        help="Phrase count or indices per tier (e.g. '1', '2', '1 2', '2 3 4', '1-3', '0' for all 10)",
    )
    parser.add_argument(
        "--ref",
        type=str,
        default="",
        help="Custom reference audio path (if not using --voice)",
    )
    parser.add_argument(
        "--ref-text",
        type=str,
        default="",
        help="Custom reference transcript (if not using --voice)",
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
        help="Diffusion steps (default: 8)",
    )
    parser.add_argument(
        "--cfg",
        type=float,
        default=2.0,
        help="CFG guidance strength (default: 2.0)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed multiplier (default: 1.0)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run batch workers in parallel across multiple processes",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Number of parallel worker processes (default: 2)",
    )

    args = parser.parse_args()
    json_path = Path(args.voices_json)

    if args.list_voices:
        cmd_list(json_path)
        return

    if args.list_prompts:
        cmd_prompts(args.prompts_file)
        return

    cmd_batch(
        voice_key=args.voice if not args.ref else "",
        ref_audio=args.ref,
        ref_text=args.ref_text,
        lang=args.lang,
        tier=args.tier,
        count=args.count,
        prompts_file=args.prompts_file,
        audio_format=args.format,
        steps=args.steps,
        cfg=args.cfg,
        speed=args.speed,
        parallel=args.parallel,
        workers=args.workers,
        json_path=json_path,
    )


if __name__ == "__main__":
    main()
