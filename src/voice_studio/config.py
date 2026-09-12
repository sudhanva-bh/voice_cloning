"""
Global configuration, paths, and constants for Voice Studio.
"""

from pathlib import Path
import sys
import codecs

# UTF-8 unbuffered output configuration on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True, write_through=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True, write_through=True)
    except AttributeError:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Root paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = REPO_ROOT / "models"
SAMPLES_DIR = REPO_ROOT / "samples"
ADDED_DIR = SAMPLES_DIR / "added"
GENERATED_DIR = REPO_ROOT / "generated"
BATCHES_DIR = GENERATED_DIR / "batches"

VOICES_JSON = SAMPLES_DIR / "voices.json"
PROMPTS_JSON = REPO_ROOT / "prompts.json"

# IndicF5 Model Constants
INDICF5_DIR = MODELS_DIR / "indicf5"
SAFETENSORS_PATH = INDICF5_DIR / "model.safetensors"
VOCAB_PATH = INDICF5_DIR / "vocab.txt"
SAMPLE_RATE = 24000
HOP_LENGTH = 256

# ZipVoice English Constants
ZIPVOICE_DIR = REPO_ROOT / "sherpa-onnx-zipvoice-distill-int8-zh-en-emilia"
VOCOS_ONNX_PATH = REPO_ROOT / "vocos_24khz.onnx"

# Add scratch/indicf5_repo to sys.path for F5-TTS architecture dependencies
SCRATCH_REPO = REPO_ROOT / "scratch" / "indicf5_repo"
if SCRATCH_REPO.is_dir() and str(SCRATCH_REPO) not in sys.path:
    sys.path.insert(0, str(SCRATCH_REPO))


def get_next_batch_dir(base_dir: Path = BATCHES_DIR) -> Path:
    """Finds the next incremental batch directory (e.g. generated/batches/batch-1, batch-2, etc.)."""
    base_dir.mkdir(parents=True, exist_ok=True)
    existing = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("batch-")]
    indices = []
    for d in existing:
        try:
            indices.append(int(d.name.split("-")[1]))
        except (IndexError, ValueError):
            pass
    next_idx = max(indices, default=0) + 1
    batch_dir = base_dir / f"batch-{next_idx}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    return batch_dir

