"""
Indic Voice Studio — Zero-Shot Neural Voice Cloning & Reference Catalog Engine.
"""

__version__ = "1.0.0"

from .catalog.manager import VoiceCatalog
from .dataset.prompts import PromptsDataset
from .audio.io import save_audio, get_audio_info, normalize_audio_rms

__all__ = [
    "VoiceCatalog",
    "PromptsDataset",
    "IndicF5Engine",
    "IndicF5BatchRunner",
    "ZipVoiceEngine",
    "save_audio",
    "get_audio_info",
    "normalize_audio_rms",
]


def __getattr__(name: str):
    """Lazy-load neural engines on demand to keep CLI startup instant."""
    if name == "IndicF5Engine":
        from .engines.indicf5 import IndicF5Engine
        return IndicF5Engine
    elif name == "IndicF5BatchRunner":
        from .engines.batch_indicf5 import IndicF5BatchRunner
        return IndicF5BatchRunner
    elif name == "ZipVoiceEngine":
        from .engines.zipvoice import ZipVoiceEngine
        return ZipVoiceEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
