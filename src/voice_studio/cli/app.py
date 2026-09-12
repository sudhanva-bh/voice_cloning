"""
Main Argparse CLI application router for Voice Studio.
"""

import argparse
from pathlib import Path
from ..config import VOICES_JSON, PROMPTS_JSON
from .commands import (
    cmd_list,
    cmd_info,
    cmd_add,
    cmd_delete,
    cmd_clone,
    cmd_batch,
    cmd_prompts,
)
from .interactive import interactive_shell


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voice_studio",
        description="Indic Voice Studio — Neural Voice Cloning & Catalog CLI",
        epilog="Run without subcommands to launch the interactive menu.",
    )
    parser.add_argument(
        "--json",
        type=str,
        default=str(VOICES_JSON),
        help="Path to voices.json catalog (default: samples/voices.json)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. list
    subparsers.add_parser("list", help="List all registered voices and audio health status")

    # 2. info
    info_p = subparsers.add_parser("info", help="Inspect voice details and spoken transcript")
    info_p.add_argument("key", type=str, help="Voice key to inspect")

    # 3. prompts
    prompts_p = subparsers.add_parser("prompts", help="Browse available phrases dataset in prompts.json")
    prompts_p.add_argument("--file", "-f", type=str, default=str(PROMPTS_JSON), help="Path to prompts JSON file")

    # 4. add
    add_p = subparsers.add_parser("add", help="Add/register a new reference audio file into catalog")
    add_p.add_argument("--audio", "-a", type=str, required=True, help="Path to source audio file (.wav/.mp3/.ogg/.m4a)")
    add_p.add_argument("--key", "-k", type=str, default="", help="Voice key identifier")
    add_p.add_argument("--transcript", "-t", type=str, required=True, help="Exact transcript of the reference audio")
    add_p.add_argument("--desc", "-d", type=str, default="", help="Description or speaker style notes")
    add_p.add_argument("--move", "-m", action="store_true", help="Move file instead of copying to samples/added/")

    # 5. delete
    del_p = subparsers.add_parser("delete", help="Delete a voice key from catalog")
    del_p.add_argument("key", type=str, help="Voice key to delete")
    del_p.add_argument("--delete-audio", action="store_true", help="Also delete audio file from disk")

    # 6. clone
    clone_p = subparsers.add_parser("clone", help="Run IndicF5 single-utterance voice cloning")
    clone_p.add_argument("--voice", "-v", type=str, default="", help="Preset voice key from catalog")
    clone_p.add_argument("--ref", type=str, default="", help="Path to reference audio file")
    clone_p.add_argument("--ref-text", type=str, default="", help="Transcript of reference audio")
    clone_p.add_argument("--text", "-t", type=str, default="", help="Target text to synthesize")
    clone_p.add_argument("--out", "-o", type=str, default="", help="Output audio file path")
    clone_p.add_argument("--format", "-f", type=str, default="wav", choices=["wav", "mp3", "ogg", "flac"], help="Output format (default: wav)")
    clone_p.add_argument("--steps", type=int, default=8, help="Diffusion steps (default: 8)")
    clone_p.add_argument("--cfg", type=float, default=2.0, help="CFG strength (default: 2.0)")
    clone_p.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier (default: 1.0)")

    # 7. batch
    batch_p = subparsers.add_parser("batch", help="Run IndicF5 customizable batch synthesis from prompts.json")
    batch_p.add_argument("--voice", "-v", type=str, default="", help="Preset voice key from catalog")
    batch_p.add_argument("--ref", type=str, default="", help="Path to reference audio file")
    batch_p.add_argument("--ref-text", type=str, default="", help="Transcript of reference audio")
    batch_p.add_argument("--lang", "--language", type=str, default="all", help="Language filter: 'all', '1 2', 'telugu,tamil'")
    batch_p.add_argument("--tier", "--length", type=str, default="all", help="Tier filter: 'all', '2-4', 'short,medium'")
    batch_p.add_argument("--count", "--limit", type=str, default="1", help="Count or indices per tier (e.g. '1', '1-3', '1 2', '0')")
    batch_p.add_argument("--prompts-file", type=str, default=str(PROMPTS_JSON), help="Path to prompts JSON file")
    batch_p.add_argument("--format", "-f", type=str, default="wav", choices=["wav", "mp3", "ogg", "flac"], help="Output format (default: wav)")
    batch_p.add_argument("--steps", type=int, default=8, help="Diffusion steps (default: 8)")
    batch_p.add_argument("--cfg", type=float, default=2.0, help="CFG strength (default: 2.0)")
    batch_p.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    batch_p.add_argument("--parallel", action="store_true", help="Run batch workers in parallel")
    batch_p.add_argument("--workers", type=int, default=2, help="Number of parallel worker processes (default: 2)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    json_path = Path(args.json)

    if args.command == "list":
        cmd_list(json_path)
    elif args.command == "info":
        cmd_info(args.key, json_path)
    elif args.command == "prompts":
        cmd_prompts(args.file)
    elif args.command == "add":
        cmd_add(
            audio_path_str=args.audio,
            voice_key=args.key,
            transcript=args.transcript,
            description=args.desc,
            move_file=args.move,
            json_path=json_path,
        )
    elif args.command == "delete":
        cmd_delete(args.key, delete_audio=args.delete_audio, json_path=json_path)
    elif args.command == "clone":
        cmd_clone(
            voice_key=args.voice,
            ref_audio=args.ref,
            ref_text=args.ref_text,
            target_text=args.text,
            out_path=args.out,
            audio_format=args.format,
            steps=args.steps,
            cfg=args.cfg,
            speed=args.speed,
            json_path=json_path,
        )
    elif args.command == "batch":
        cmd_batch(
            voice_key=args.voice,
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
    else:
        interactive_shell(json_path)


if __name__ == "__main__":
    main()
