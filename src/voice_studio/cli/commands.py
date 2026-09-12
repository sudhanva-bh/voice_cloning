"""
Action handlers for Voice Studio CLI subcommands.
"""

from pathlib import Path
from ..config import VOICES_JSON, PROMPTS_JSON, GENERATED_DIR, get_next_batch_dir
from ..catalog.manager import VoiceCatalog, sanitize_key
from ..dataset.prompts import PromptsDataset


def cmd_list(json_path: Path = VOICES_JSON):
    """Displays formatted table of all registered voices and their audio file health."""
    catalog = VoiceCatalog(json_path)
    entries = catalog.catalog

    print("\n" + "=" * 85)
    print(f" REGISTERED VOICES CATALOG ({len(entries)} voices) — {Path(json_path).name}")
    print("=" * 85)
    if not entries:
        print("  (Catalog is currently empty. Use 'add' to register a new voice.)")
        print("=" * 85 + "\n")
        return

    print(f" {'#':<3} | {'Voice Key':<26} | {'Audio File':<32} | {'Dur':<6} | {'Status'}")
    print("-" * 85)
    for i, (key, info) in enumerate(entries.items()):
        audio_rel = info.get("audio", "")
        _, exists = catalog.resolve_audio_path(audio_rel)
        status = "[Ready]" if exists else "[Missing]"
        dur = f"{info['duration_sec']:.1f}s" if "duration_sec" in info else "--"
        audio_display = Path(audio_rel).name
        print(f" {i+1:<3} | {key:<26} | {audio_display:<32} | {dur:<6} | {status}")

    print("=" * 85 + "\n")


def cmd_info(voice_key: str, json_path: Path = VOICES_JSON):
    """Displays details, transcript, and audio status for a specific voice key."""
    catalog = VoiceCatalog(json_path)
    clean = sanitize_key(voice_key)
    voice = catalog.get_voice(clean)

    if not voice:
        print(f"\n[Error] Voice key '{clean}' not found in catalog.")
        print(f"Available keys: {', '.join(catalog.catalog.keys())}\n")
        return

    audio_path = voice.get("audio", "")
    full_path = voice.get("resolved_audio_path", "")
    exists = voice.get("audio_exists", False)

    print("\n" + "=" * 75)
    print(f" VOICE DETAILS: '{clean}'")
    print("=" * 75)
    print(f"  Key          : {clean}")
    print(f"  Description  : {voice.get('description', 'N/A')}")
    print(f"  Audio Path   : {audio_path}")
    print(f"  Resolved At  : {full_path} [{'Exists' if exists else 'Missing'}]")
    if "duration_sec" in voice:
        print(f"  Duration     : {voice['duration_sec']:.2f} seconds")
    if "added_at" in voice:
        print(f"  Added Date   : {voice['added_at']}")
    print("-" * 75)
    print("  Reference Transcript (Spoken Text):")
    print(f"  \"{voice.get('transcript', '')}\"")
    print("-" * 75)
    print("  Quick Test Command:")
    print(f"  python clone.py --voice {clean} --text \"<YOUR_TARGET_TEXT>\"")
    print("=" * 75 + "\n")


def cmd_add(
    audio_path_str: str,
    voice_key: str,
    transcript: str,
    description: str = "",
    move_file: bool = False,
    json_path: Path = VOICES_JSON,
) -> str:
    """Ingests audio, moves/copies to samples/added/, and updates voices.json."""
    catalog = VoiceCatalog(json_path)
    try:
        clean_key, dest_path = catalog.register_voice(
            audio_path_str=audio_path_str,
            voice_key=voice_key,
            transcript=transcript,
            description=description,
            move_file=move_file,
        )
        print("\n" + "=" * 75)
        print(f" [OK] VOICE REGISTERED SUCCESSFULLY: '{clean_key}'")
        print("=" * 75)
        print(f"  Catalog File : {json_path}")
        print(f"  Audio Saved  : {dest_path}")
        print(f"  Voice Key    : {clean_key}")
        print(f"  Transcript   : \"{transcript}\"")
        print("=" * 75 + "\n")
        return clean_key
    except Exception as e:
        print(f"\n[Error] Failed to register voice: {e}\n")
        return ""


def cmd_delete(voice_key: str, delete_audio: bool = False, json_path: Path = VOICES_JSON):
    """Deletes a voice from voices.json and optionally disk."""
    catalog = VoiceCatalog(json_path)
    clean = sanitize_key(voice_key)
    if catalog.delete_voice(clean, delete_audio_file=delete_audio):
        print(f"\n[OK] Successfully removed voice '{clean}' from catalog.")
        if delete_audio:
            print("  (Associated audio file was also deleted from disk)")
        print()
    else:
        print(f"\n[Error] Voice key '{clean}' not found in catalog.\n")


def cmd_prompts(prompts_file: str = str(PROMPTS_JSON)):
    """Browses dataset in prompts.json."""
    ds = PromptsDataset(prompts_file)
    data = ds.data
    if not data:
        print(f"\n[Error] No prompts found at: {prompts_file}\n")
        return

    total = sum(len(phrases) for tiers in data.values() for phrases in tiers.values())
    print("\n" + "=" * 85)
    print(f" CONVERSATIONAL PHRASES DATASET ({total} Total Sentences) — {Path(prompts_file).name}")
    print("=" * 85)

    for lang, tiers in data.items():
        print(f"\n Language: {lang.upper()}")
        print("-" * 40)
        for tier, phrases in tiers.items():
            print(f"  [{tier.upper()}] ({len(phrases)} phrases):")
            for idx, p in enumerate(phrases):
                print(f"    {idx+1}. {p}")
    print("=" * 85 + "\n")


def cmd_clone(
    voice_key: str = "",
    ref_audio: str = "",
    ref_text: str = "",
    target_text: str = "",
    out_path: str = "",
    audio_format: str = "wav",
    steps: int = 8,
    cfg: float = 2.0,
    speed: float = 1.0,
    json_path: Path = VOICES_JSON,
):
    """Executes single utterance voice cloning."""
    if voice_key:
        catalog = VoiceCatalog(json_path)
        v = catalog.get_voice(voice_key)
        if not v:
            print(f"[Error] Voice key '{voice_key}' not found.")
            return
        if not v["audio_exists"]:
            print(f"[Error] Audio file missing for '{voice_key}': {v['resolved_audio_path']}")
            return
        ref_audio = v["resolved_audio_path"]
        ref_text = v.get("transcript", "")
        print(f"[Preset Voice] Loaded voice '{voice_key}'")

    if not ref_audio or not ref_text:
        print("[Error] Reference audio and reference transcript are required.")
        return

    if not target_text:
        target_text = "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் இப்போது உங்கள் குரலில் பேசுகிறேன்."

    fmt = audio_format.lower() if audio_format else "wav"
    if not out_path:
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        key_stem = sanitize_key(voice_key) if voice_key else Path(ref_audio).stem
        out_path = str(GENERATED_DIR / f"{key_stem}_cloned.{fmt}")

    from ..engines.indicf5 import IndicF5Engine
    engine = IndicF5Engine()
    res = engine.synthesize(
        reference_audio_path=ref_audio,
        reference_text=ref_text,
        target_text=target_text,
        output_wav_path=out_path,
        audio_format=fmt,
        num_steps=steps,
        cfg_strength=cfg,
        speed=speed,
    )
    print("\n" + "=" * 70)
    print(f" [OK] Synthesis Complete: {res['output_path']}")
    print(f"  Duration: {res['duration_sec']:.2f}s | Gen Time: {res['elapsed_sec']:.2f}s | RTF: {res['rtf']:.2f}x")
    print("=" * 70 + "\n")


def cmd_batch(
    voice_key: str = "",
    ref_audio: str = "",
    ref_text: str = "",
    lang: str = "all",
    tier: str = "all",
    count: str = "1",
    prompts_file: str = str(PROMPTS_JSON),
    audio_format: str = "wav",
    steps: int = 8,
    cfg: float = 2.0,
    speed: float = 1.0,
    parallel: bool = False,
    workers: int = 2,
    json_path: Path = VOICES_JSON,
):
    """Executes batch voice cloning synthesis."""
    if voice_key:
        catalog = VoiceCatalog(json_path)
        v = catalog.get_voice(voice_key)
        if not v:
            print(f"[Error] Voice key '{voice_key}' not found.")
            return
        if not v["audio_exists"]:
            print(f"[Error] Audio file missing for '{voice_key}': {v['resolved_audio_path']}")
            return
        ref_audio = v["resolved_audio_path"]
        ref_text = v.get("transcript", "")
        print(f"[Preset Voice] Loaded voice '{voice_key}'")

    if not ref_audio or not ref_text:
        print("[Error] Reference audio and reference transcript are required.")
        return

    ds = PromptsDataset(prompts_file)
    selected_prompts = ds.load(
        languages=lang,
        categories=tier,
        count_per_category=count,
        audio_format=audio_format,
    )

    if not selected_prompts:
        print(f"[Error] No phrases matched filter: lang='{lang}', tier='{tier}', count='{count}'")
        return

    batch_dir = get_next_batch_dir()
    prompts_with_paths = {
        text: str(batch_dir / fn)
        for text, fn in selected_prompts.items()
    }

    from ..engines.batch_indicf5 import IndicF5BatchRunner
    runner = IndicF5BatchRunner()
    if parallel:
        results, init_time = runner.run_parallel(
            prompts_dict=prompts_with_paths,
            batch_dir=batch_dir,
            ref_audio=ref_audio,
            ref_text=ref_text,
            num_steps=steps,
            cfg=cfg,
            speed=speed,
            audio_format=audio_format,
            workers=workers,
        )
    else:
        results, init_time = runner.run_sequential(
            prompts_dict=prompts_with_paths,
            batch_dir=batch_dir,
            ref_audio=ref_audio,
            ref_text=ref_text,
            num_steps=steps,
            cfg=cfg,
            speed=speed,
            audio_format=audio_format,
        )

    # Summary
    total_audio_sec = sum(res["duration_sec"] for _, res in results)
    total_synth_sec = sum(res["elapsed_sec"] for _, res in results)
    avg_rtf = total_synth_sec / max(total_audio_sec, 0.01)

    print("=" * 85)
    print(f" [Batch Completed] Batch Synthesis Summary ({len(results)} files)")
    print(f" Output Folder : {batch_dir.resolve()}")
    print("=" * 85)
    print(f"{'#':<3} | {'Output File':<42} | {'Audio Len':<10} | {'Gen Time':<10} | {'RTF':<8}")
    print("-" * 85)
    for i, (_, res) in enumerate(results):
        rel_path = Path(res['output_path']).name
        print(f"{i+1:<3} | {rel_path:<42} | {res['duration_sec']:>7.2f} s | {res['elapsed_sec']:>7.2f} s | {res['rtf']:>6.2f}x")
    print("-" * 85)
    print(f" Total Audio Generated : {total_audio_sec:.2f} seconds")
    print(f" Total Generation Time : {total_synth_sec:.2f} seconds (Avg Speed: {avg_rtf:.2f}x RTF)")
    if init_time > 0:
        saved_io_time = (len(results) - 1) * init_time
        print(f" One-Time Cold Load    : {init_time:.2f}s (Saved ~{saved_io_time:.2f}s redundant 1.35GB I/O!)")
    print("=" * 85 + "\n")
