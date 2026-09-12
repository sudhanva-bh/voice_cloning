"""
Multilingual phrases dataset manager supporting multi-selection tokens,
number lists ('1 2'), hyphenated ranges ('2-4'), and format mapping.
"""

import json
from pathlib import Path
from ..config import PROMPTS_JSON

LANG_MAP = {
    "1": "telugu", "telugu": "telugu", "te": "telugu",
    "2": "tamil", "tamil": "tamil", "ta": "tamil",
    "3": "hindi", "hindi": "hindi", "hi": "hindi",
}

TIER_MAP = {
    "1": "short", "short": "short", "s": "short",
    "2": "medium", "medium": "medium", "med": "medium", "m": "medium",
    "3": "midlong", "midlong": "midlong", "mid-long": "midlong", "mid_long": "midlong", "ml": "midlong",
    "4": "long", "long": "long", "l": "long",
}


def parse_multi_selection(input_val, mapping: dict, default_all: list) -> list:
    """
    Parses space-separated, comma-separated, range, or number/keyword tokens
    (e.g. '1 2', '2-4', '1-3', 'telugu, tamil').
    """
    if input_val is None:
        return default_all
    if isinstance(input_val, list):
        return [mapping.get(str(x).lower(), str(x).lower()) for x in input_val if str(x).lower() in mapping or str(x).lower() in default_all]

    val_str = str(input_val).strip()
    if not val_str or val_str.lower() in ("0", "all", "*"):
        return default_all

    tokens = [t.strip().lower() for t in val_str.replace(",", " ").split() if t.strip()]
    selected = []
    for t in tokens:
        if "-" in t:
            parts = t.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                start = int(parts[0])
                end = int(parts[1])
                for num_i in range(min(start, end), max(start, end) + 1):
                    key_str = str(num_i)
                    if key_str in mapping:
                        res = mapping[key_str]
                        if res not in selected:
                            selected.append(res)
                continue
        if t in mapping:
            res = mapping[t]
            if res not in selected:
                selected.append(res)
        elif t in default_all:
            if t not in selected:
                selected.append(t)
    return selected if selected else default_all


def parse_phrase_indices(input_val, max_available: int = 10) -> list:
    """
    Parses count integer, space-separated indices ('1 2', '1 2 3', '2 3 4'), ranges ('1-4'), or 'all'/'0'.
    """
    if input_val is None:
        return [0]

    val_str = str(input_val).strip().lower()
    if not val_str or val_str in ("0", "all", "*"):
        return list(range(max_available))

    # Single integer count (e.g. 2 means first 2 phrases)
    if val_str.isdigit():
        count = int(val_str)
        if count == 0 or count >= max_available:
            return list(range(max_available))
        return list(range(min(count, max_available)))

    indices = []
    tokens = [t.strip() for t in val_str.replace(",", " ").split() if t.strip()]
    for t in tokens:
        if "-" in t:
            parts = t.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                start = max(1, int(parts[0]))
                end = min(max_available, int(parts[1]))
                for i in range(start, end + 1):
                    if (i - 1) not in indices:
                        indices.append(i - 1)
        elif t.isdigit():
            idx = int(t) - 1
            if 0 <= idx < max_available and idx not in indices:
                indices.append(idx)
    return sorted(indices) if indices else [0]


class PromptsDataset:
    """Loads and filters conversational phrases from prompts.json."""

    def __init__(self, json_path: Path | str = PROMPTS_JSON):
        self.json_path = Path(json_path)
        self.data = self._load_data()

    def _load_data(self) -> dict:
        if not self.json_path.is_file():
            alt = Path("data/prompts.json")
            if alt.is_file():
                self.json_path = alt
            else:
                return {}
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load(
        self,
        languages="all",
        categories="all",
        count_per_category="1",
        audio_format: str = "wav",
    ) -> dict[str, str]:
        """
        Returns a dictionary mapping { 'Target phrase text': 'output_filename.ext' }
        according to language, tier, and count/index filters.
        """
        default_langs = ["telugu", "tamil", "hindi"]
        default_cats = ["short", "medium", "midlong", "long"]

        req_langs = parse_multi_selection(languages, LANG_MAP, default_langs)
        req_cats = parse_multi_selection(categories, TIER_MAP, default_cats)

        ext = audio_format.lower().replace(".", "")
        selected_prompts = {}

        for lang in req_langs:
            lang_data = self.data.get(lang, {})
            for cat in req_cats:
                phrases = lang_data.get(cat, [])
                if not phrases:
                    continue
                indices = parse_phrase_indices(count_per_category, len(phrases))
                for idx in indices:
                    if 0 <= idx < len(phrases):
                        clean_text = phrases[idx].strip()
                        filename = f"{lang}_{cat}_{idx+1}.{ext}"
                        selected_prompts[clean_text] = filename

        return selected_prompts
