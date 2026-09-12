"""
Interactive Terminal UI (TUI) menu shell for Voice Studio.
"""

from pathlib import Path
from ..config import VOICES_JSON
from ..catalog.manager import VoiceCatalog, sanitize_key
from .commands import (
    cmd_list,
    cmd_info,
    cmd_add,
    cmd_delete,
    cmd_clone,
    cmd_batch,
    cmd_prompts,
)


def interactive_shell(json_path: Path = VOICES_JSON):
    """Rich interactive menu loop for Voice Studio."""
    catalog_mgr = VoiceCatalog(json_path)

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
            catalog = catalog_mgr.load()
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
            catalog = catalog_mgr.load()
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

            cmd_clone(
                voice_key=key,
                target_text=target_text,
                audio_format=audio_format,
                steps=steps,
                json_path=json_path,
            )

        elif choice == "5":
            catalog = catalog_mgr.load()
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
            catalog = catalog_mgr.load()
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
