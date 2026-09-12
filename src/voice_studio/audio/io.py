"""
Audio I/O utilities supporting WAV, MP3, OGG, and FLAC serialization,
RMS normalization, and metadata probing.
"""

from pathlib import Path
import wave
import torch
import soundfile as sf
from ..config import SAMPLE_RATE


def save_audio(out_path: str | Path, wav, sample_rate: int = SAMPLE_RATE, fmt: str = "wav") -> Path:
    """
    Saves audio waveform tensor/numpy array to disk with the requested container format.
    Supports 'wav', 'mp3', 'ogg', 'flac'.
    """
    path = Path(out_path)
    if fmt and fmt.lower() in ("wav", "mp3", "ogg", "flac"):
        if path.suffix.lower().replace(".", "") != fmt.lower():
            path = path.with_suffix(f".{fmt.lower()}")
    
    ext = path.suffix.lower().replace(".", "")
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert torch tensor to numpy if needed
    if isinstance(wav, torch.Tensor):
        wav = wav.detach().cpu().squeeze().numpy()

    if ext == "mp3":
        sf.write(str(path), wav, samplerate=sample_rate, format="MP3")
    elif ext in ("ogg", "oga"):
        sf.write(str(path), wav, samplerate=sample_rate, format="OGG")
    elif ext == "flac":
        sf.write(str(path), wav, samplerate=sample_rate, format="FLAC")
    else:
        sf.write(str(path), wav, samplerate=sample_rate, subtype="PCM_16")
        
    return path


def probe_duration(file_path: Path | str) -> float | None:
    """Attempts fast duration probing via wave / soundfile without loading raw PCM into RAM."""
    path = Path(file_path)
    if not path.is_file():
        return None
    try:
        with sf.SoundFile(str(path)) as sf_file:
            return float(sf_file.frames) / float(sf_file.samplerate)
    except Exception:
        pass

    try:
        with wave.open(str(path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return float(frames) / float(rate)
    except Exception:
        return None


def get_audio_info(file_path: Path | str) -> dict:
    """Returns sample rate, channels, frames, and duration metadata for an audio file."""
    path = Path(file_path)
    info = {"exists": path.is_file(), "path": str(path)}
    if not path.is_file():
        return info
    try:
        with sf.SoundFile(str(path)) as sf_file:
            info["samplerate"] = sf_file.samplerate
            info["channels"] = sf_file.channels
            info["frames"] = sf_file.frames
            info["duration"] = float(sf_file.frames) / float(sf_file.samplerate)
            info["format"] = sf_file.format
            info["subtype"] = sf_file.subtype
    except Exception as e:
        info["duration"] = probe_duration(path)
        info["error"] = str(e)
    return info


def normalize_audio_rms(audio_tensor: torch.Tensor, target_rms: float = 0.1) -> torch.Tensor:
    """Normalizes audio RMS amplitude to target RMS level (default 0.1)."""
    rms = torch.sqrt(torch.mean(torch.square(audio_tensor)))
    if rms < target_rms and rms.item() > 1e-6:
        return audio_tensor * (target_rms / rms.item())
    return audio_tensor
