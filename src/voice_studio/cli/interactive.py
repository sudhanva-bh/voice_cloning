"""
Interactive Terminal User Interface (TUI) for Indic Voice Studio.
Features instant hotkeys (press 1-7, 0, q to trigger immediately),
arrow-key navigation, spacebar multi-selection toggles,
Explorer-style typeahead voice search (e.g. typing 'deep' jumps to deep_classic),
and in-place single-line phrase counter with dynamic dataset limits.
"""

import sys
import time
import string
from pathlib import Path
import questionary
from questionary import Choice, Style

from ..config import VOICES_JSON, PROMPTS_JSON
from ..catalog.manager import VoiceCatalog, sanitize_key
from ..dataset.prompts import PromptsDataset
from .commands import (
    cmd_list,
    cmd_info,
    cmd_add,
    cmd_delete,
    cmd_clone,
    cmd_batch,
    cmd_prompts,
)

# Custom visual theme styling
CUSTOM_STYLE = Style([
    ("qmark", "fg:#7c4dff bold"),         # Question mark / accent
    ("question", "bold fg:#ffffff"),      # Question text
    ("answer", "fg:#00e676 bold"),        # Selected answer
    ("pointer", "fg:#7c4dff bold"),       # Pointer arrow
    ("highlighted", "fg:#7c4dff bold"),   # Highlighted item
    ("selected", "fg:#00e676"),           # Selected checkbox
    ("separator", "fg:#616161"),          # Separator lines
    ("instruction", "fg:#9e9e9e italic"), # Help instructions
    ("text", "fg:#e0e0e0"),               # Normal text
])


def _enable_windows_ansi():
    """Ensures ANSI escape sequences are enabled on Windows console."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


def prompt_counter(
    message: str = "How many phrases per tier:",
    default: int = 1,
    min_val: int = 1,
    max_val: int = 10,
) -> int:
    """
    In-place single-line interactive counter.
    Pressing Up/Right increments, Down/Left decrements, digits set directly, Enter confirms.
    """
    _enable_windows_ansi()
    val = max(min_val, min(default, max_val))

    QMARK = "\033[95m?\033[0m"
    QUESTION = f"\033[1m{message}\033[0m"

    def render(current_val: int, final: bool = False):
        if final:
            sys.stdout.write(f"\r{QMARK} {QUESTION} \033[92m\033[1m{current_val}\033[0m\033[K\n")
            sys.stdout.flush()
        else:
            bounds = f"\033[90m(1-{max_val})\033[0m"
            ans = f"\033[92m\033[1m{current_val}\033[0m"
            sys.stdout.write(f"\r{QMARK} {QUESTION} {ans} {bounds}\033[K")
            sys.stdout.flush()

    try:
        if sys.platform == "win32":
            import msvcrt
            render(val)
            while True:
                ch = msvcrt.getch()
                if ch in (b"\xe0", b"\x00"):
                    ch2 = msvcrt.getch()
                    if ch2 in (b"H", b"M"):  # Up or Right arrow
                        if val < max_val:
                            val += 1
                            render(val)
                    elif ch2 in (b"P", b"K"):  # Down or Left arrow
                        if val > min_val:
                            val -= 1
                            render(val)
                elif ch in (b"\r", b"\n"):  # Enter
                    render(val, final=True)
                    return val
                elif ch == b"\x03":  # Ctrl+C
                    raise KeyboardInterrupt
                elif ch == b"\x1b":  # Escape
                    render(val, final=True)
                    return val
                elif ch in (b"+", b"="):
                    if val < max_val:
                        val += 1
                        render(val)
                elif ch in (b"-", b"_"):
                    if val > min_val:
                        val -= 1
                        render(val)
                elif ch.isdigit():
                    num = int(ch.decode())
                    if min_val <= num <= max_val:
                        val = num
                        render(val)
        else:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                render(val)
                while True:
                    ch = sys.stdin.read(1)
                    if ch == "\x1b":
                        seq = sys.stdin.read(2)
                        if seq in ("[A", "[C"):  # Up or Right arrow
                            if val < max_val:
                                val += 1
                                render(val)
                        elif seq in ("[B", "[D"):  # Down or Left arrow
                            if val > min_val:
                                val -= 1
                                render(val)
                    elif ch in ("\r", "\n"):
                        render(val, final=True)
                        return val
                    elif ch == "\x03":
                        raise KeyboardInterrupt
                    elif ch.isdigit():
                        num = int(ch)
                        if min_val <= num <= max_val:
                            val = num
                            render(val)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        raw = input(f" {message} [1-{max_val}] (default: {val}): ").strip()
        if raw.isdigit():
            val = max(min_val, min(int(raw), max_val))
        return val


def _select_voice(catalog_mgr: VoiceCatalog, prompt_msg: str = "Select a reference voice:") -> str | None:
    """Displays an interactive scrollable list of registered voices with Windows Explorer-style typeahead search."""
    catalog = catalog_mgr.load()
    if not catalog:
        print("\n (Catalog is currently empty. Please register a reference voice first.)\n")
        return None

    choices = []
    for key, info in catalog.items():
        audio_rel = info.get("audio", "")
        _, exists = catalog_mgr.resolve_audio_path(audio_rel)
        missing_tag = " [Missing]" if not exists else ""
        dur_str = f"{info['duration_sec']:.1f}s" if "duration_sec" in info else ""
        desc_str = f" - {info.get('description', '')}" if info.get("description") else ""
        dur_tag = f" ({dur_str})" if dur_str else ""

        display_label = f"{key:<26}{dur_tag:<8}{desc_str}{missing_tag}"
        choices.append(Choice(title=display_label, value=key))

    choices.append(Choice(title="[Back] Return to Main Menu", value=None))

    try:
        q = questionary.select(
            prompt_msg,
            choices=choices,
            style=CUSTOM_STYLE,
            use_arrow_keys=True,
            instruction=" ",
        )

        windows = q.application.layout.find_all_windows()
        ic = next((w.content for w in windows if hasattr(w.content, "pointed_at")), None)

        search_state = {"buffer": "", "time": 0.0}
        TIMEOUT = 0.9  # Timeout in seconds to reset search buffer

        def typeahead_search(char: str):
            if ic is None:
                return
            now = time.time()
            if now - search_state["time"] > TIMEOUT:
                search_state["buffer"] = ""
            search_state["time"] = now

            ch_low = char.lower()

            # Handle single key repeated cycling (e.g. s -> s -> s)
            if len(search_state["buffer"]) == 1 and search_state["buffer"] == ch_low:
                start_idx = (ic.pointed_at + 1) % len(choices)
                for offset in range(len(choices)):
                    check_idx = (start_idx + offset) % len(choices)
                    c = choices[check_idx]
                    val_str = str(c.value or c.title).lower()
                    if val_str.startswith(ch_low):
                        ic.pointed_at = check_idx
                        return
                return

            search_state["buffer"] += ch_low
            buf = search_state["buffer"]

            # 1. Exact prefix match on voice key or title
            for idx, c in enumerate(choices):
                val_str = str(c.value or c.title).lower()
                if val_str.startswith(buf):
                    ic.pointed_at = idx
                    return

            # 2. Substring match
            for idx, c in enumerate(choices):
                val_str = str(c.value or c.title).lower()
                if buf in val_str:
                    ic.pointed_at = idx
                    return

        def handle_backspace():
            if ic is None or not search_state["buffer"]:
                return
            search_state["buffer"] = search_state["buffer"][:-1]
            buf = search_state["buffer"]
            if buf:
                for idx, c in enumerate(choices):
                    val_str = str(c.value or c.title).lower()
                    if val_str.startswith(buf) or buf in val_str:
                        ic.pointed_at = idx
                        return

        kb = q.application.key_bindings

        # Register letter and digit keys for instant typeahead jumping (Windows Explorer style)
        allowed_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + "_-"
        for char_item in allowed_chars:
            @kb.add(char_item, eager=True)
            def _(event, ch=char_item):
                typeahead_search(ch)

        @kb.add("backspace", eager=True)
        def _(event):
            handle_backspace()

        @kb.add("escape", eager=True)
        def _(event):
            event.app.exit(result=None)

        return q.ask()
    except Exception:
        print(f"\n Available Keys: {', '.join(catalog.keys())}")
        raw = input(f" {prompt_msg} ").strip()
        clean = sanitize_key(raw)
        return clean if clean in catalog else None


def ask_main_menu() -> str | None:
    """Prompts main menu supporting both instant numeric hotkeys (1-7, 0, q) and arrow-key navigation."""
    choices = [
        Choice(title="[1] List All Registered Voices", value="list"),
        Choice(title="[2] Add New Reference Voice", value="add"),
        Choice(title="[3] Inspect Voice Details & Transcript", value="info"),
        Choice(title="[4] Test Single Voice Clone", value="clone"),
        Choice(title="[5] Run Customizable Batch Synthesis", value="batch"),
        Choice(title="[6] Browse Available Phrases Dataset", value="prompts"),
        Choice(title="[7] Delete / Unregister a Voice", value="delete"),
        Choice(title="[0] Exit", value="exit"),
    ]

    try:
        q = questionary.select(
            "Select an option [1-7, 0]:",
            choices=choices,
            style=CUSTOM_STYLE,
            use_arrow_keys=True,
            instruction=" ",
        )

        kb = q.application.key_bindings

        # Instant numeric hotkey listeners (fires immediately upon pressing key)
        @kb.add("1", eager=True)
        def _(event):
            event.app.exit(result="list")

        @kb.add("2", eager=True)
        def _(event):
            event.app.exit(result="add")

        @kb.add("3", eager=True)
        def _(event):
            event.app.exit(result="info")

        @kb.add("4", eager=True)
        def _(event):
            event.app.exit(result="clone")

        @kb.add("5", eager=True)
        def _(event):
            event.app.exit(result="batch")

        @kb.add("6", eager=True)
        def _(event):
            event.app.exit(result="prompts")

        @kb.add("7", eager=True)
        def _(event):
            event.app.exit(result="delete")

        @kb.add("0", eager=True)
        @kb.add("q", eager=True)
        def _(event):
            event.app.exit(result="exit")

        return q.ask()
    except Exception:
        # Graceful fallback for non-TTY / redirected terminals
        print("\n  [1] List All Registered Voices")
        print("  [2] Add New Reference Voice")
        print("  [3] Inspect Voice Details")
        print("  [4] Test Single Voice Clone")
        print("  [5] Run Customizable Batch Synthesis")
        print("  [6] Browse Phrases Dataset")
        print("  [7] Delete / Unregister a Voice")
        print("  [0] Exit\n")
        raw = input(" Select an option [0-7]: ").strip().lower()
        mapping = {
            "1": "list", "2": "add", "3": "info", "4": "clone",
            "5": "batch", "6": "prompts", "7": "delete", "0": "exit", "q": "exit",
        }
        return mapping.get(raw, None)


def interactive_shell(json_path: Path = VOICES_JSON):
    """Clean interactive CLI menu loop for Voice Studio."""
    catalog_mgr = VoiceCatalog(json_path)

    while True:
        print("\n" + "=" * 80)
        print(" INDIC VOICE STUDIO - NEURAL VOICE CLONING & CATALOG")
        print("=" * 80)

        main_action = ask_main_menu()

        if main_action is None or main_action == "exit":
            print("\n Goodbye.\n")
            break

        # ==========================================
        # 1. LIST VOICES
        # ==========================================
        if main_action == "list":
            cmd_list(json_path)

        # ==========================================
        # 2. ADD NEW VOICE
        # ==========================================
        elif main_action == "add":
            print("\n" + "-" * 70)
            print(" ADD NEW REFERENCE VOICE")
            print("-" * 70)
            try:
                audio_input = questionary.text(
                    "Audio file path (.wav, .mp3, .ogg, .m4a):",
                    validate=lambda val: True if val.strip() else "Audio path cannot be empty.",
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()
            except Exception:
                audio_input = input(" Audio file path: ").strip()

            if not audio_input:
                continue

            path_obj = Path(audio_input.strip().strip("'\"")).expanduser().resolve()
            if not path_obj.is_file():
                print(f"\n [Error] File not found at: {path_obj}\n")
                continue

            default_key = sanitize_key(path_obj.stem)
            try:
                key_input = questionary.text(
                    "Voice Identifier / Key:",
                    default=default_key,
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()
            except Exception:
                key_input = input(f" Voice Key [{default_key}]: ").strip()
            voice_key = sanitize_key(key_input) if key_input else default_key

            try:
                transcript_input = questionary.text(
                    "Spoken Reference Transcript (Exact spoken text):",
                    validate=lambda val: True if val.strip() else "Transcript cannot be empty.",
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()
            except Exception:
                transcript_input = input(" Spoken Reference Transcript: ").strip()

            if not transcript_input:
                continue

            try:
                desc_input = questionary.text(
                    "Speaker Style / Description (optional):",
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()
            except Exception:
                desc_input = input(" Description (optional): ").strip()

            try:
                mode_choice = questionary.select(
                    "File Storage Mode:",
                    choices=[
                        Choice(title="Copy file to samples/added/ (Keeps original)", value=False),
                        Choice(title="Move file to samples/added/ (Deletes original)", value=True),
                    ],
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()
                move_file = bool(mode_choice)
            except Exception:
                move_file = False

            cmd_add(
                audio_path_str=str(path_obj),
                voice_key=voice_key,
                transcript=transcript_input,
                description=desc_input if desc_input else "",
                move_file=move_file,
                json_path=json_path,
            )

        # ==========================================
        # 3. INSPECT VOICE
        # ==========================================
        elif main_action == "info":
            selected_key = _select_voice(catalog_mgr, "Select voice to inspect:")
            if selected_key:
                cmd_info(voice_key=selected_key, json_path=json_path)

        # ==========================================
        # 4. SINGLE VOICE CLONE
        # ==========================================
        elif main_action == "clone":
            selected_key = _select_voice(catalog_mgr, "Select voice for single cloning:")
            if not selected_key:
                continue

            default_text = "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் இப்போது உங்கள் குரலில் பேசுகிறேன்."
            try:
                target_text = questionary.text(
                    "Target text to synthesize:",
                    default=default_text,
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()
            except Exception:
                target_text = input(f" Target text [{default_text}]: ").strip()
            if not target_text:
                target_text = default_text

            try:
                audio_format = questionary.select(
                    "Output container format:",
                    choices=[
                        Choice(title="MP3 (.mp3) - Compressed & universal", value="mp3"),
                        Choice(title="WAV (.wav) - Uncompressed 16-bit PCM", value="wav"),
                        Choice(title="OGG (.ogg) - High-quality Vorbis", value="ogg"),
                        Choice(title="FLAC (.flac) - Lossless compression", value="flac"),
                    ],
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()
            except Exception:
                audio_format = "mp3"
            if not audio_format:
                audio_format = "mp3"

            try:
                steps_choice = questionary.select(
                    "Euler ODE Diffusion Steps:",
                    choices=[
                        Choice(title="8 steps (Recommended - Fast on CPU, high quality)", value=8),
                        Choice(title="4 steps (Ultra-Fast - 2x faster, slight quality tradeoff)", value=4),
                        Choice(title="16 steps (Maximum Quality - Studio fidelity)", value=16),
                        Choice(title="Custom step count...", value="custom"),
                    ],
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()

                if steps_choice == "custom":
                    custom_steps = questionary.text(
                        "Enter custom step count [4-64]:",
                        default="8",
                        style=CUSTOM_STYLE,
                        instruction=" ",
                    ).ask()
                    steps = int(custom_steps) if custom_steps and custom_steps.isdigit() else 8
                else:
                    steps = steps_choice if steps_choice else 8
            except Exception:
                steps = 8

            cmd_clone(
                voice_key=selected_key,
                target_text=target_text,
                audio_format=audio_format,
                steps=steps,
                json_path=json_path,
            )

        # ==========================================
        # 5. BATCH SYNTHESIS
        # ==========================================
        elif main_action == "batch":
            selected_key = _select_voice(catalog_mgr, "Select reference voice for batch synthesis:")
            if not selected_key:
                continue

            try:
                # Multi-select Languages with Checkboxes (Space to toggle)
                selected_langs = questionary.checkbox(
                    "Select language(s) to synthesize:",
                    choices=[
                        Choice(title="Telugu", value="telugu", checked=True),
                        Choice(title="Tamil", value="tamil", checked=True),
                        Choice(title="Hindi", value="hindi", checked=False),
                    ],
                    style=CUSTOM_STYLE,
                    validate=lambda sel: True if len(sel) > 0 else "Select at least one language.",
                    instruction=" ",
                ).ask()
            except Exception:
                raw_langs = input(" Languages [0=All, 1=Telugu, 2=Tamil, 3=Hindi] (e.g. 1 2): ").strip()
                selected_langs = [raw_langs] if raw_langs else ["telugu", "tamil"]

            if not selected_langs:
                continue

            try:
                # Multi-select Length Tiers with Checkboxes (Space to toggle)
                selected_tiers = questionary.checkbox(
                    "Select duration / length tier(s):",
                    choices=[
                        Choice(title="Short (~3s, ~15-30 chars)", value="short", checked=False),
                        Choice(title="Medium (~5s, ~40-70 chars)", value="medium", checked=True),
                        Choice(title="Mid-long (~8s, ~80-120 chars)", value="midlong", checked=True),
                        Choice(title="Long (~12s, ~130-180 chars)", value="long", checked=True),
                    ],
                    style=CUSTOM_STYLE,
                    validate=lambda sel: True if len(sel) > 0 else "Select at least one length tier.",
                    instruction=" ",
                ).ask()
            except Exception:
                raw_tiers = input(" Tiers [0=All, 1=Short, 2=Medium, 3=Midlong, 4=Long] (e.g. 2-4): ").strip()
                selected_tiers = [raw_tiers] if raw_tiers else ["medium", "midlong", "long"]

            if not selected_tiers:
                continue

            # Dynamic phrase limit bounded by source dataset
            ds = PromptsDataset(PROMPTS_JSON)
            max_available = 10
            if ds.data:
                limits = [
                    len(ds.data.get(lang, {}).get(tier, []))
                    for lang in selected_langs
                    for tier in selected_tiers
                    if ds.data.get(lang, {}).get(tier, [])
                ]
                if limits:
                    max_available = max(limits)

            # In-place single-line phrase counter (Up increments, Down decrements, Enter submits)
            count_val = prompt_counter(
                message="How many phrases per tier:",
                default=1,
                min_val=1,
                max_val=max_available,
            )
            selected_count = str(count_val)

            try:
                # Output Format
                audio_format = questionary.select(
                    "Output container format:",
                    choices=[
                        Choice(title="MP3 (.mp3) - Compressed & lightweight", value="mp3"),
                        Choice(title="WAV (.wav) - Uncompressed 16-bit PCM", value="wav"),
                        Choice(title="OGG (.ogg) - High-quality Vorbis", value="ogg"),
                        Choice(title="FLAC (.flac) - Lossless compression", value="flac"),
                    ],
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()
            except Exception:
                audio_format = "mp3"
            if not audio_format:
                audio_format = "mp3"

            try:
                # Steps Selection
                steps_choice = questionary.select(
                    "Euler ODE Diffusion Steps:",
                    choices=[
                        Choice(title="8 steps (Recommended - Balanced speed & fidelity)", value=8),
                        Choice(title="4 steps (Ultra-Fast - 2x speed for quick prototyping)", value=4),
                        Choice(title="16 steps (Maximum Quality - Studio master)", value=16),
                        Choice(title="Custom step count...", value="custom"),
                    ],
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()

                if steps_choice == "custom":
                    custom_steps = questionary.text(
                        "Enter custom step count [4-64]:",
                        default="8",
                        style=CUSTOM_STYLE,
                        instruction=" ",
                    ).ask()
                    steps = int(custom_steps) if custom_steps and custom_steps.isdigit() else 8
                else:
                    steps = steps_choice if steps_choice else 8
            except Exception:
                steps = 8

            lang_param = " ".join(selected_langs)
            tier_param = " ".join(selected_tiers)

            cmd_batch(
                voice_key=selected_key,
                lang=lang_param,
                tier=tier_param,
                count=selected_count,
                audio_format=audio_format,
                steps=steps,
                json_path=json_path,
            )

        # ==========================================
        # 6. BROWSE PROMPTS
        # ==========================================
        elif main_action == "prompts":
            cmd_prompts()

        # ==========================================
        # 7. DELETE VOICE
        # ==========================================
        elif main_action == "delete":
            selected_key = _select_voice(catalog_mgr, "Select voice to DELETE:")
            if not selected_key:
                continue

            try:
                confirm = questionary.confirm(
                    f"Are you sure you want to delete '{selected_key}' from the catalog?",
                    default=False,
                    style=CUSTOM_STYLE,
                    instruction=" ",
                ).ask()

                if confirm:
                    del_file = questionary.confirm(
                        "Also delete the audio recording file from disk?",
                        default=False,
                        style=CUSTOM_STYLE,
                        instruction=" ",
                    ).ask()
                    cmd_delete(voice_key=selected_key, delete_audio=del_file, json_path=json_path)
            except Exception:
                pass
