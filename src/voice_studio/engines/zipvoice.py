"""
Sherpa-ONNX English/Multilingual Zero-Shot TTS engine with ZipVoice-Distill INT8 ONNX and Vocos.
"""

import time
from pathlib import Path
from datetime import datetime
import librosa
import soundfile as sf
import sherpa_onnx

from ..config import ZIPVOICE_DIR, VOCOS_ONNX_PATH, GENERATED_DIR
from ..audio.io import save_audio


class ZipVoiceEngine:
    """Encapsulates the Sherpa-ONNX ZipVoice pipeline for ultra-fast English TTS."""

    def __init__(
        self,
        model_dir: Path | str = ZIPVOICE_DIR,
        vocoder_path: Path | str = VOCOS_ONNX_PATH,
        num_threads: int = 2,
    ):
        self.model_dir = Path(model_dir)
        self.vocoder_path = Path(vocoder_path)
        self.num_threads = num_threads
        self.tts = self._create_tts()

    def _create_tts(self) -> sherpa_onnx.OfflineTts:
        tokens_path = self.model_dir / "tokens.txt"
        encoder_path = self.model_dir / "encoder.int8.onnx"
        decoder_path = self.model_dir / "decoder.int8.onnx"
        espeak_path = self.model_dir / "espeak-ng-data"
        lexicon_path = self.model_dir / "lexicon.txt"

        if not tokens_path.is_file():
            raise FileNotFoundError(f"ZipVoice model files missing at: {self.model_dir}")

        tts_config = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                zipvoice=sherpa_onnx.OfflineTtsZipvoiceModelConfig(
                    tokens=str(tokens_path),
                    encoder=str(encoder_path),
                    decoder=str(decoder_path),
                    data_dir=str(espeak_path),
                    lexicon=str(lexicon_path),
                    vocoder=str(self.vocoder_path),
                ),
                debug=False,
                num_threads=self.num_threads,
                provider="cpu",
            )
        )
        if not tts_config.validate():
            raise ValueError("Sherpa-ONNX ZipVoice configuration failed validation.")

        return sherpa_onnx.OfflineTts(tts_config)

    def generate(
        self,
        text: str,
        reference_audio_path: str | Path,
        reference_text: str = "",
        output_path: str | Path | None = None,
        audio_format: str = "wav",
        num_steps: int = 4,
    ) -> dict:
        """Synthesizes English text cloned from reference audio."""
        ref_p = Path(reference_audio_path)
        if not ref_p.is_file():
            raise FileNotFoundError(f"Reference audio not found: {ref_p}")

        reference_audio, sample_rate = librosa.load(str(ref_p), sr=None)

        gen_config = sherpa_onnx.GenerationConfig()
        gen_config.reference_audio = reference_audio
        gen_config.reference_sample_rate = sample_rate
        if reference_text:
            gen_config.reference_text = reference_text
        gen_config.num_steps = num_steps
        gen_config.extra["min_char_in_sentence"] = "30"

        start = time.time()
        audio = self.tts.generate(text, gen_config)
        elapsed = time.time() - start

        if len(audio.samples) == 0:
            raise RuntimeError("Sherpa-ONNX ZipVoice failed to produce audio samples.")

        duration_sec = len(audio.samples) / audio.sample_rate
        rtf = elapsed / max(duration_sec, 0.01)

        if output_path is None:
            GENERATED_DIR.mkdir(parents=True, exist_ok=True)
            ref_stem = ref_p.stem
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = GENERATED_DIR / f"{ref_stem}_zipvoice_{ts}.{audio_format}"

        saved_file = save_audio(
            output_path,
            audio.samples,
            sample_rate=audio.sample_rate,
            fmt=audio_format,
        )

        return {
            "output_path": str(saved_file),
            "elapsed_sec": elapsed,
            "duration_sec": duration_sec,
            "rtf": rtf,
            "sample_rate": audio.sample_rate,
        }
