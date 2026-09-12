"""
Voice catalog manager handling voices.json CRUD operations, audio path resolution,
and audio file ingestion into samples/added/.
"""

import json
import re
import shutil
import time
from pathlib import Path
from datetime import datetime

from ..config import VOICES_JSON, SAMPLES_DIR, ADDED_DIR
from ..audio.io import get_audio_info


def sanitize_key(name: str) -> str:
    """Normalizes arbitrary string into a clean lowercase identifier (e.g. 'Tamil Pangram' -> 'tamil_pangram')."""
    clean = re.sub(r"[^\w\-_]", "_", name.strip().lower())
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean


class VoiceCatalog:
    """Manages the registered reference voices in voices.json."""

    def __init__(self, json_path: Path | str = VOICES_JSON):
        self.json_path = Path(json_path)
        self.catalog = self.load()

    def load(self) -> dict:
        """Loads and parses voices.json, returning an empty dict if the file does not exist."""
        if not self.json_path.is_file():
            return {}
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save(self):
        """Serializes current catalog dictionary to voices.json formatted with indentation."""
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.catalog, f, ensure_ascii=False, indent=2)

    def resolve_audio_path(self, rel_or_abs_path: str | Path) -> tuple[Path, bool]:
        """Resolves relative audio paths across candidate locations in the repository."""
        p = Path(rel_or_abs_path)
        if p.is_file():
            return p.resolve(), True

        candidates = [
            self.json_path.parent / p,
            SAMPLES_DIR / p,
            ADDED_DIR / p,
            SAMPLES_DIR / "tamil_voices" / p.name,
            ADDED_DIR / p.name,
            SAMPLES_DIR / p.name,
        ]
        for c in candidates:
            if c.is_file():
                return c.resolve(), True

        return (self.json_path.parent / p).resolve(), False

    def get_voice(self, voice_key: str) -> dict | None:
        """Fetches voice entry dictionary for a given key, resolving audio path."""
        clean = sanitize_key(voice_key)
        entry = self.catalog.get(clean)
        if not entry:
            return None
        
        audio_path, exists = self.resolve_audio_path(entry.get("audio", ""))
        entry_copy = dict(entry)
        entry_copy["key"] = clean
        entry_copy["resolved_audio_path"] = str(audio_path)
        entry_copy["audio_exists"] = exists
        return entry_copy

    def register_voice(
        self,
        audio_path_str: str,
        voice_key: str,
        transcript: str,
        description: str = "",
        move_file: bool = False,
    ) -> tuple[str, str]:
        """
        Ingests and validates a new reference audio file, copies/moves it into samples/added/,
        and writes the entry to voices.json.
        """
        raw_path = audio_path_str.strip().strip("'\"")
        src_path = Path(raw_path).expanduser().resolve()

        if not src_path.is_file():
            raise FileNotFoundError(f"Audio file does not exist at: {src_path}")

        clean_key = sanitize_key(voice_key) if voice_key else sanitize_key(src_path.stem)
        if not clean_key:
            clean_key = f"voice_{int(time.time())}"

        # Analyze audio properties
        info = get_audio_info(src_path)
        duration = info.get("duration")

        ADDED_DIR.mkdir(parents=True, exist_ok=True)
        extension = src_path.suffix.lower()
        dest_filename = f"{clean_key}{extension}"
        dest_path = ADDED_DIR / dest_filename

        if src_path != dest_path:
            if move_file:
                shutil.move(str(src_path), str(dest_path))
            else:
                shutil.copy2(str(src_path), str(dest_path))

        rel_audio_path = f"samples/added/{dest_filename}"
        new_entry = {
            "audio": rel_audio_path,
            "transcript": transcript.strip(),
            "description": description.strip() if description else f"Registered voice '{clean_key}'",
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if duration is not None:
            new_entry["duration_sec"] = round(duration, 3)

        self.catalog[clean_key] = new_entry
        self.save()
        return clean_key, str(dest_path)

    def delete_voice(self, voice_key: str, delete_audio_file: bool = False) -> bool:
        """Removes a voice from voices.json and optionally deletes the audio file from disk."""
        clean = sanitize_key(voice_key)
        if clean not in self.catalog:
            return False

        entry = self.catalog.pop(clean)
        self.save()

        if delete_audio_file:
            audio_path, exists = self.resolve_audio_path(entry.get("audio", ""))
            if exists and audio_path.is_file():
                try:
                    audio_path.unlink()
                except Exception:
                    pass
        return True
