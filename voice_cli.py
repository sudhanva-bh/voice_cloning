#!/usr/bin/env python3
"""
Indic Voice Studio — Unified CLI Program for Voice Management & Neural Voice Cloning
Provides an interactive menu-driven interface and scriptable subcommands for:
- Adding/registering reference audio (auto-validation, duration check, moving/copying to samples/added/)
- Listing and inspecting registered voices in samples/voices.json
- Direct voice cloning testing (IndicF5 single utterance & batch synthesis)
- Voice catalog maintenance and deletion

Usage:
    # 1. Interactive Menu-Driven CLI Program:
    .\\sherpa-env\\Scripts\\python.exe voice_cli.py

    # 2. Subcommands (Scriptable CLI Mode):
    .\\sherpa-env\\Scripts\\python.exe voice_cli.py list
    .\\sherpa-env\\Scripts\\python.exe voice_cli.py add --audio "samples/sudhanva_voic_clone.wav" --key "my_voice" --transcript "..." --desc "..."
    .\\sherpa-env\\Scripts\\python.exe voice_cli.py info deep_classic
    .\\sherpa-env\\Scripts\\python.exe voice_cli.py test deep_classic --text "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?"
    .\\sherpa-env\\Scripts\\python.exe voice_cli.py batch deep_classic --steps 8
    .\\sherpa-env\\Scripts\\python.exe voice_cli.py delete my_voice
"""

import os
import sys
import json
import shutil
import codecs
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Force UTF-8 unbuffered output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True, write_through=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True, write_through=True)
    except AttributeError:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Override print to flush immediately
_orig_print = print
def print(*args, **kwargs):
    kwargs.setdefault("flush", True)
    _orig_print(*args, **kwargs)

# Default Project Paths
REPO_ROOT = Path(__file__).resolve().parent
SAMPLES_DIR = REPO_ROOT / "samples"
ADDED_DIR = SAMPLES_DIR / "added"
VOICES_JSON = SAMPLES_DIR / "voices.json"
PYTHON_EXE = sys.executable


# ==============================================================================
# HELPER UTILITIES
# ==============================================================================

def sanitize_key(key: str) -> str:
    """Sanitizes voice key to clean lowercase alphanumeric + underscore format."""
    clean = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in key.strip().lower())
    clean = "_".join(filter(None, clean.split("_")))
    return clean


def get_audio_info(file_path: Path) -> dict:
    """Inspects audio duration, sample rate, channels, and format."""
    try:
        import soundfile as sf
        info = sf.info(str(file_path))
        return {
            "duration": info.duration,
            "samplerate": info.samplerate,
            "channels": info.channels,
            "format": info.format,
        }
    except Exception:
        try:
            import librosa
            y, sr = librosa.load(str(file_path), sr=None, mono=False)
            channels = 1 if y.ndim == 1 else y.shape[0]
            duration = librosa.get_duration(y=y, sr=sr)
            return {
                "duration": duration,
                "samplerate": sr,
                "channels": channels,
                "format": file_path.suffix.upper().replace(".", ""),
            }
        except Exception as e:
            return {
                "duration": None,
                "samplerate": None,
                "channels": None,
                "format": file_path.suffix.upper().replace(".", ""),
                "error": str(e),
            }


def load_catalog(json_path: Path = VOICES_JSON) -> dict:
    """Loads existing voices.json with fallback resolution."""
    if not json_path.is_file():
        alt = SAMPLES_DIR / "tamil_voices" / "voices.json"
        if alt.is_file():
            json_path = alt
        else:
            return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to read {json_path}: {e}")
        return {}


def save_catalog(data: dict, json_path: Path = VOICES_JSON):
    """Saves catalog data to voices.json with UTF-8 encoding and clean indentation."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def resolve_audio_file(audio_path_str: str) -> tuple[Path, bool]:
    """Resolves audio path whether absolute, relative to repo root, or in subfolders."""
    raw = Path(audio_path_str)
    if raw.is_file():
        return raw.resolve(), True
    candidates = [
        REPO_ROOT / audio_path_str,
        SAMPLES_DIR / audio_path_str,
        ADDED_DIR / raw.name,
        SAMPLES_DIR / "tamil_voices" / raw.name,
        SAMPLES_DIR / raw.name,
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve(), True
    return raw, False


# ==============================================================================
# CORE OPERATIONS
# ==============================================================================

def cmd_list(json_path: Path = VOICES_JSON):
    """Lists all registered voices in formatted table view."""
    catalog = load_catalog(json_path)
    print("\n" + "=" * 85)
    print(f" 📋 REGISTERED VOICES CATALOG ({len(catalog)} voices) — {json_path.name}")
    print("=" * 85)
    if not catalog:
        print("  (Catalog is currently empty. Use 'add' to register a new voice.)")
        print("=" * 85 + "\n")
        return

    print(f" {'#':<3} | {'Voice Key':<26} | {'Audio File':<32} | {'Dur':<6} | {'Status'}")
    print("-" * 85)
    for i, (key, info) in enumerate(catalog.items()):
        audio_rel = info.get("audio", "")
        _, exists = resolve_audio_file(audio_rel)
        status = "✓ Ready" if exists else "✗ Missing"
        dur = f"{info['duration_sec']:.1f}s" if "duration_sec" in info else "--"
        audio_display = Path(audio_rel).name
        print(f" {i+1:<3} | {key:<26} | {audio_display:<32} | {dur:<6} | {status}")

    print("=" * 85 + "\n")


def cmd_info(voice_key: str, json_path: Path = VOICES_JSON):
    """Displays comprehensive details, transcript, and audio health for a specific voice key."""
    catalog = load_catalog(json_path)
    clean = sanitize_key(voice_key)
    if clean not in catalog:
        print(f"\n[Error] Voice key '{clean}' not found in catalog.")
        print(f"Available keys: {', '.join(catalog.keys())}\n")
        return

    entry = catalog[clean]
    audio_path = entry.get("audio", "")
    full_path, exists = resolve_audio_file(audio_path)

    print("\n" + "=" * 75)
    print(f" 🎙️  VOICE DETAILS: '{clean}'")
    print("=" * 75)
    print(f"  Key          : {clean}")
    print(f"  Description  : {entry.get('description', 'N/A')}")
    print(f"  Audio Path   : {audio_path}")
    print(f"  Resolved At  : {full_path} [{'✓ File Exists' if exists else '✗ File Missing'}]")
    if "duration_sec" in entry:
        print(f"  Duration     : {entry['duration_sec']:.2f} seconds")
    if "added_at" in entry:
        print(f"  Added Date   : {entry['added_at']}")
    print("-" * 75)
    print("  Reference Transcript (Spoken Text):")
    print(f"  \"{entry.get('transcript', '')}\"")
    print("-" * 75)
    print("  Quick Test Command:")
    print(f"  .\\sherpa-env\\Scripts\\python.exe test_indicf5_clone.py --voice {clean} --text \"<YOUR_TARGET_TEXT>\"")
    print("=" * 75 + "\n")


def cmd_add(
    audio_path_str: str,
    voice_key: str,
    transcript: str,
    description: str = "",
    move_file: bool = False,
    json_path: Path = VOICES_JSON,
) -> str:
    """Adds, validates, moves/copies audio to samples/added/, and registers in voices.json."""
    raw_path = audio_path_str.strip().strip("'\"")
    src_path = Path(raw_path).expanduser().resolve()

    if not src_path.is_file():
        print(f"\n[Error] Audio file does not exist at: {src_path}\n")
        return ""

    clean_key = sanitize_key(voice_key) if voice_key else sanitize_key(src_path.stem)
    if not clean_key:
        clean_key = f"voice_{int(time.time())}"

    # Analyze audio file
    info = get_audio_info(src_path)
    duration = info.get("duration")
    sr = info.get("samplerate", 24000)
    ch = info.get("channels", 1)

    print("\n" + "=" * 75)
    print(f" 📥 REGISTERING NEW VOICE: '{clean_key}'")
    print("=" * 75)
    print(f"  Source Audio File : {src_path}")
    if duration is not None:
        print(f"  Audio Properties  : Duration: {duration:.2f}s | Sample Rate: {sr} Hz | Channels: {ch}")
        if duration < 2.5:
            print("  ⚠️ [Notice] Audio duration is under 2.5s. Voice cloning quality improves with 3.5s - 6.0s reference clips.")
        elif duration > 8.0:
            print("  ⚠️ [Notice] Audio duration exceeds 8.0s. IndicF5 diffusion works best with 3.5s - 6.0s clips for tight text-mel alignment.")
        else:
            print("  ✓ [Optimal] Duration is within the golden range (3.0s - 7.0s) for high-fidelity IndicF5 diffusion!")

    # Target in samples/added/
    ADDED_DIR.mkdir(parents=True, exist_ok=True)
    extension = src_path.suffix.lower()
    dest_filename = f"{clean_key}{extension}"
    dest_path = ADDED_DIR / dest_filename

    if src_path != dest_path:
        if move_file:
            print(f"  Moving audio      : {src_path.name} ➔ samples/added/{dest_filename}")
            shutil.move(str(src_path), str(dest_path))
        else:
            print(f"  Copying audio     : {src_path.name} ➔ samples/added/{dest_filename}")
            shutil.copy2(str(src_path), str(dest_path))
    else:
        print(f"  Audio is already placed in: samples/added/{dest_filename}")

    rel_audio_path = f"samples/added/{dest_filename}".replace("\\", "/")

    # Update catalog
    catalog = load_catalog(json_path)
    entry = {
        "audio": rel_audio_path,
        "transcript": transcript.strip(),
        "description": description.strip() if description else f"Registered Voice ({clean_key})",
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if duration is not None:
        entry["duration_sec"] = round(duration, 2)

    catalog[clean_key] = entry
    save_catalog(catalog, json_path)

    print("=" * 75)
    print(f" ✅ SUCCESS! Voice '{clean_key}' registered successfully in {json_path.name}")
    print(f"  Saved Location    : {rel_audio_path}")
    print(f"  Transcript        : {transcript.strip()}")
    print("-" * 75)
    print(" Test it right now with:")
    print(f"   .\\sherpa-env\\Scripts\\python.exe voice_cli.py test {clean_key} --text \"<YOUR_TARGET_TEXT>\"")
    print("=" * 75 + "\n")

    return clean_key


def cmd_delete(voice_key: str, delete_audio: bool = False, json_path: Path = VOICES_JSON):
    """Unregisters a voice key from voices.json and optionally deletes the audio file."""
    catalog = load_catalog(json_path)
    clean = sanitize_key(voice_key)
    if clean not in catalog:
        print(f"\n[Error] Voice key '{clean}' not found in catalog.\n")
        return

    entry = catalog.pop(clean)
    save_catalog(catalog, json_path)
    print(f"\n[Success] Removed voice '{clean}' from {json_path.name}.")

    if delete_audio and "audio" in entry:
        audio_file, exists = resolve_audio_file(entry["audio"])
        if exists:
            try:
                audio_file.unlink()
                print(f"[Deleted] Audio file deleted: {audio_file}")
            except Exception as e:
                print(f"[Warning] Could not delete file: {e}")
    print()


def cmd_test(
    voice_key: str,
    target_text: str = "",
    out_path: str = "",
    audio_format: str = "wav",
    steps: int = 8,
    cfg: float = 2.0,
    speed: float = 1.0,
    json_path: Path = VOICES_JSON,
):
    """Executes single-utterance voice cloning test using IndicF5 engine."""
    catalog = load_catalog(json_path)
    clean = sanitize_key(voice_key)
    if clean not in catalog:
        print(f"\n[Error] Voice key '{clean}' not found in catalog.")
        print(f"Available keys: {', '.join(catalog.keys())}\n")
        return

    if not target_text:
        target_text = "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் இப்போது உங்கள் குரலில் பேசுகிறேன்."

    fmt = audio_format.lower() if audio_format else "wav"
    if not out_path:
        out_dir = REPO_ROOT / "generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / f"{clean}_output.{fmt}")

    print("\n" + "=" * 75)
    print(f" 🚀 Running IndicF5 Voice Cloning Test for '{clean}'")
    print("=" * 75)
    print(f"  Target Text   : \"{target_text}\"")
    print(f"  Output Format : {fmt.upper()}")
    print(f"  Output Path   : {out_path}")
    print(f"  Steps / CFG   : {steps} steps | CFG {cfg} | Speed {speed}x")
    print("-" * 75 + "\n")

    cmd = [
        PYTHON_EXE,
        str(REPO_ROOT / "test_indicf5_clone.py"),
        "--voice", clean,
        "--voices-json", str(json_path),
        "--text", target_text,
        "--out", out_path,
        "--format", fmt,
        "--steps", str(steps),
        "--cfg", str(cfg),
        "--speed", str(speed),
    ]

    subprocess.run(cmd)


def cmd_prompts(prompts_file: str = "prompts.json"):
    """Displays all available phrases in the prompts.json dataset."""
    path = Path(prompts_file)
    if not path.is_file():
        alt = Path("data/prompts.json")
        if alt.is_file():
            path = alt
        else:
            print(f"[Error] Prompts file not found at: {prompts_file}")
            return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("\n" + "=" * 85)
    print(f" 📖 AVAILABLE BATCH PHRASES CATALOG — {path.resolve()}")
    print("=" * 85)
    for lang, tiers in data.items():
        print(f"\n Language: {lang.upper()}")
        print("-" * 40)
        for tier, phrases in tiers.items():
            print(f"  [{tier.upper()}] ({len(phrases)} phrases):")
            for idx, p in enumerate(phrases):
                print(f"    {idx+1}. {p}")
    print("=" * 85 + "\n")


def cmd_batch(
    voice_key: str,
    lang: str = "all",
    tier: str = "all",
    count: str = "1",
    prompts_file: str = "prompts.json",
    audio_format: str = "wav",
    steps: int = 8,
    cfg: float = 2.0,
    speed: float = 1.0,
    json_path: Path = VOICES_JSON,
):
    """Runs batch synthesis across customizable prompts from prompts.json."""
    clean = sanitize_key(voice_key)
    fmt = audio_format.lower() if audio_format else "wav"
    count_str = str(count).strip()
    count_display = count_str if count_str not in ("0", "all", "*") else "ALL 10 per tier"
    print("\n" + "=" * 75)
    print(f" 🚀 Launching IndicF5 Batch Synthesis for '{clean}' ({fmt.upper()})")
    print(f"  Languages : {lang.upper()} | Tiers: {tier.upper()} | Count/Indices: {count_display}")
    print("=" * 75 + "\n")

    cmd = [
        PYTHON_EXE,
        str(REPO_ROOT / "test_batch_indicf5.py"),
        "--voice", clean,
        "--voices-json", str(json_path),
        "--prompts-file", prompts_file,
        "--lang", str(lang),
        "--tier", str(tier),
        "--count", str(count),
        "--format", fmt,
        "--steps", str(steps),
        "--cfg", str(cfg),
        "--speed", str(speed),
    ]

    subprocess.run(cmd)


# ==============================================================================
# INTERACTIVE CLI PROGRAM SHELL (TUI)
# ==============================================================================

def interactive_shell(json_path: Path = VOICES_JSON):
    """Rich interactive menu loop for the Voice Studio CLI program."""
    while True:
        print("\n" + "=" * 80)
        print(" 🎙️  INDIC VOICE STUDIO — CLONING & CATALOG CLI")
        print("=" * 80)
        print("  [1] 📋 List All Registered Voices")
        print("  [2] ➕ Add New Reference Voice (Auto-Validate & Move to samples/added/)")
        print("  [3] 🔍 Inspect Voice Details & Spoken Transcript")
        print("  [4] 🧪 Test Single Voice Clone (IndicF5 Single Utterance)")
        print("  [5] ⚡ Run Customizable Batch Synthesis (Telugu, Tamil, Hindi)")
        print("  [6] 📖 Browse Available Phrases Dataset (prompts.json)")
        print("  [7] 🗑️  Delete / Unregister a Voice")
        print("  [0] 🚪 Exit")
        print("=" * 80)

        choice = input(" Select an option [0-7]: ").strip()

        if choice == "1":
            cmd_list(json_path)

        elif choice == "2":
            print("\n" + "-" * 70)
            print(" ➕ ADD NEW REFERENCE VOICE")
            print("-" * 70)
            audio_input = input(" 1. Audio file path (.wav, .mp3, .ogg, .m4a): ").strip().strip("'\"")
            if not audio_input:
                print(" [Error] Audio path cannot be empty.")
                continue
            path_obj = Path(audio_input).expanduser().resolve()
            if not path_obj.is_file():
                print(f" [Error] File not found at: {path_obj}")
                continue

            default_key = sanitize_key(path_obj.stem)
            key_input = input(f" 2. Voice Identifier / Key [{default_key}]: ").strip()
            voice_key = sanitize_key(key_input) if key_input else default_key

            transcript_input = input(" 3. Spoken Reference Transcript: ").strip()
            if not transcript_input:
                print(" [Error] Transcript cannot be empty.")
                continue

            desc_input = input(" 4. Speaker Style / Description (optional): ").strip()
            mode_input = input(" 5. Copy or Move audio to samples/added/? [c=Copy, m=Move] (default: Copy): ").strip().lower()
            move_file = mode_input.startswith("m")

            cmd_add(
                audio_path_str=str(path_obj),
                voice_key=voice_key,
                transcript=transcript_input,
                description=desc_input,
                move_file=move_file,
                json_path=json_path,
            )

        elif choice == "3":
            catalog = load_catalog(json_path)
            if not catalog:
                print("\n (Catalog is empty.)")
                continue
            print("\n Available Keys: " + ", ".join(catalog.keys()))
            key = input(" Enter Voice Key to inspect: ").strip()
            if not key or sanitize_key(key) not in catalog:
                print(f" [Error] Invalid key '{key}'.")
                continue
            cmd_info(voice_key=key, json_path=json_path)

        elif choice == "4":
            catalog = load_catalog(json_path)
            if not catalog:
                print("\n (Catalog is empty. Add a voice first.)")
                continue
            print("\n Available Keys: " + ", ".join(catalog.keys()))
            key = input(" Enter Voice Key to test: ").strip()
            if not key or sanitize_key(key) not in catalog:
                print(f" [Error] Invalid key '{key}'.")
                continue

            default_text = "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் இப்போது உங்கள் குரலில் பேசுகிறேன்."
            text_input = input(f" Enter target text to synthesize [{default_text}]: ").strip()
            target_text = text_input if text_input else default_text

            fmt_input = input(" Enter output format [wav / mp3 / ogg / flac] (default: wav): ").strip().lower()
            audio_format = fmt_input if fmt_input in ("wav", "mp3", "ogg", "flac") else "wav"

            steps_input = input(" Enter diffusion steps [8]: ").strip()
            steps = int(steps_input) if steps_input.isdigit() else 8

            cmd_test(voice_key=key, target_text=target_text, audio_format=audio_format, steps=steps, json_path=json_path)

        elif choice == "5":
            catalog = load_catalog(json_path)
            if not catalog:
                print("\n (Catalog is empty. Add a voice first.)")
                continue
            print("\n Available Keys: " + ", ".join(catalog.keys()))
            key = input(" Enter Voice Key for batch generation: ").strip()
            if not key or sanitize_key(key) not in catalog:
                print(f" [Error] Invalid key '{key}'.")
                continue

            print("\n Languages:")
            print("  [0] All (Telugu, Tamil, Hindi)")
            print("  [1] Telugu")
            print("  [2] Tamil")
            print("  [3] Hindi")
            l_choice = input(" Select language(s) [0-3, e.g. '1 2'] (default: 0): ").strip()
            selected_lang = l_choice if l_choice else "all"

            print("\n Length Tiers:")
            print("  [0] All Tiers (Short, Medium, Mid-long, Long)")
            print("  [1] Short (~3s)")
            print("  [2] Medium (~5s)")
            print("  [3] Mid-long (~8s)")
            print("  [4] Long (~12s)")
            t_choice = input(" Select tier(s) [0-4, e.g. '1 2 3' or '2 3 4'] (default: 0): ").strip()
            selected_tier = t_choice if t_choice else "all"

            print("\n Phrases per Selected Tier:")
            print("  - Single number (e.g. '2' -> first 2 phrases)")
            print("  - Specific indices (e.g. '1 2', '2 3 4', '1 3 5')")
            print("  - Index range (e.g. '1-3', '2-5')")
            print("  - All 10 phrases (e.g. '0' or 'all')")
            count_input = input(" Enter phrase count or indices [default: 1]: ").strip()
            selected_count = count_input if count_input else "1"

            fmt_input = input(" Enter output format [wav / mp3 / ogg / flac] (default: wav): ").strip().lower()
            audio_format = fmt_input if fmt_input in ("wav", "mp3", "ogg", "flac") else "wav"

            steps_input = input(" Enter diffusion steps [8]: ").strip()
            steps = int(steps_input) if steps_input.isdigit() else 8

            cmd_batch(
                voice_key=key,
                lang=selected_lang,
                tier=selected_tier,
                count=selected_count,
                audio_format=audio_format,
                steps=steps,
                json_path=json_path,
            )

        elif choice == "6":
            cmd_prompts()

        elif choice == "7":
            catalog = load_catalog(json_path)
            if not catalog:
                print("\n (Catalog is empty.)")
                continue
            print("\n Available Keys: " + ", ".join(catalog.keys()))
            key = input(" Enter Voice Key to delete: ").strip()
            if not key or sanitize_key(key) not in catalog:
                print(f" [Error] Invalid key '{key}'.")
                continue
            confirm = input(f" Are you sure you want to delete '{key}'? (y/n): ").strip().lower()
            if confirm == "y":
                del_file = input(" Also delete the audio file from disk? (y/n): ").strip().lower() == "y"
                cmd_delete(voice_key=key, delete_audio=del_file, json_path=json_path)

        elif choice in ("0", "q", "exit"):
            print("\n Goodbye! 🎙️\n")
            break
        else:
            print(" Invalid choice. Please select a number from 0 to 7.")


# ==============================================================================
# MAIN ARGPARSE ENTRY POINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Indic Voice Studio CLI — Neural Voice Cloning & Reference Audio Manager",
        epilog="Run without arguments to launch the interactive menu-driven CLI program.",
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
    prompts_p.add_argument("--file", "-f", type=str, default="prompts.json", help="Path to prompts JSON file")

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

    # 6. test
    test_p = subparsers.add_parser("test", help="Run IndicF5 single-utterance voice cloning test")
    test_p.add_argument("key", type=str, help="Preset voice key from catalog")
    test_p.add_argument("--text", type=str, default="", help="Target text to synthesize")
    test_p.add_argument("--out", type=str, default="", help="Output audio file path")
    test_p.add_argument("--format", "-f", type=str, default="wav", choices=["wav", "mp3", "ogg", "flac"], help="Output audio format (default: wav)")
    test_p.add_argument("--steps", type=int, default=8, help="Euler ODE diffusion steps (default: 8)")
    test_p.add_argument("--cfg", type=float, default=2.0, help="CFG strength (default: 2.0)")
    test_p.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier (default: 1.0)")

    # 7. batch
    batch_p = subparsers.add_parser("batch", help="Run IndicF5 customizable batch synthesis from prompts.json")
    batch_p.add_argument("key", type=str, help="Preset voice key from catalog")
    batch_p.add_argument("--lang", "--language", type=str, default="all", help="Language filter: 'all', 'telugu', 'tamil', 'hindi', 'telugu,tamil'")
    batch_p.add_argument("--tier", "--length", type=str, default="all", help="Tier filter: 'all', 'short', 'medium', 'midlong', 'long'")
    batch_p.add_argument("--count", "--limit", type=str, default="1", help="Number of phrases or specific indices per tier (e.g. '1', '2', '1 2', '2 3 4', '1-4', or '0' for all)")
    batch_p.add_argument("--prompts-file", type=str, default="prompts.json", help="Path to prompts JSON file")
    batch_p.add_argument("--format", "-f", type=str, default="wav", choices=["wav", "mp3", "ogg", "flac"], help="Output audio format (default: wav)")
    batch_p.add_argument("--steps", type=int, default=8, help="Diffusion steps (default: 8)")
    batch_p.add_argument("--cfg", type=float, default=2.0, help="CFG strength (default: 2.0)")
    batch_p.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")

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
    elif args.command == "test":
        cmd_test(
            voice_key=args.key,
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
            voice_key=args.key,
            lang=args.lang,
            tier=args.tier,
            count=args.count,
            prompts_file=args.prompts_file,
            audio_format=args.format,
            steps=args.steps,
            cfg=args.cfg,
            speed=args.speed,
            json_path=json_path,
        )
    else:
        # Default to interactive CLI program menu
        interactive_shell(json_path)


if __name__ == "__main__":
    main()
