"""
Neural Voice Cloning and Text-to-Speech synthesis engines.
"""

try:
    from .indicf5 import IndicF5Engine
except ImportError:
    IndicF5Engine = None

try:
    from .batch_indicf5 import IndicF5BatchRunner
except ImportError:
    IndicF5BatchRunner = None

try:
    from .zipvoice import ZipVoiceEngine
except ImportError:
    ZipVoiceEngine = None

try:
    from .litert_indic import LiteRTIndicEngine
except ImportError:
    LiteRTIndicEngine = None

__all__ = ["IndicF5Engine", "IndicF5BatchRunner", "ZipVoiceEngine", "LiteRTIndicEngine"]
