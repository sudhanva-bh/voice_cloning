"""
IndicF5 Neural Voice Cloning Engine (AI4Bharat / F5-TTS Continuous Flow Matching DiT).
"""

import time
from pathlib import Path
import torch
import librosa
from safetensors.torch import load_file
from f5_tts.model.cfm import CFM
from f5_tts.model.backbones.dit import DiT
from f5_tts.model.utils import get_tokenizer
from vocos import Vocos

from ..config import SAFETENSORS_PATH, VOCAB_PATH, SAMPLE_RATE, HOP_LENGTH
from ..audio.io import save_audio, normalize_audio_rms


class IndicF5Engine:
    """Encapsulates the IndicF5 CFM + Vocos pipeline with warm RAM caching."""

    def __init__(
        self,
        safetensors_path: Path | str = SAFETENSORS_PATH,
        vocab_path: Path | str = VOCAB_PATH,
        verbose: bool = True,
    ):
        self.safetensors_path = Path(safetensors_path)
        self.vocab_path = Path(vocab_path)
        self.verbose = verbose
        self.torch = torch
        self._init_pipeline()

    def _init_pipeline(self):
        init_start = time.time()
        if self.verbose:
            print("  ├── [1/4] Loading Tokenizer & Vocabulary (vocab.txt)...")
        vocab_map, vocab_size = get_tokenizer(str(self.vocab_path), "custom")

        if self.verbose:
            print("  ├── [2/4] Instantiating DiT 22-Layer Backbone & CFM Graph...")
        transformer = DiT(
            dim=1024,
            depth=22,
            heads=16,
            dim_head=64,
            ff_mult=2,
            text_dim=512,
            conv_layers=4,
            text_num_embeds=vocab_size,
            mel_dim=100,
        )

        self.model = CFM(
            transformer=transformer,
            mel_spec_kwargs=dict(
                n_fft=1024,
                hop_length=256,
                win_length=1024,
                n_mel_channels=100,
                target_sample_rate=SAMPLE_RATE,
                mel_spec_type="vocos",
            ),
            odeint_kwargs=dict(method="euler"),
            vocab_char_map=vocab_map,
        )

        if self.verbose:
            print("  ├── [3/4] Reading & parsing 1.35 GB Safetensors weights into RAM...")
        weights = load_file(str(self.safetensors_path))
        clean_weights = {}
        for k, v in weights.items():
            if k.startswith("transformer."):
                clean_weights[k] = v
            elif k.startswith("ema_model.transformer."):
                clean_weights[k.replace("ema_model.transformer.", "transformer.")] = v
            else:
                clean_weights[k] = v

        self.model.load_state_dict(clean_weights, strict=False)
        self.model = self.model.eval()

        if self.verbose:
            print("  └── [4/4] Loading Vocos 24kHz Neural Vocoder...")
        self.vocoder = Vocos.from_pretrained("charactr/vocos-mel-24khz").eval()
        self.init_elapsed = time.time() - init_start
        if self.verbose:
            print(f" [ONE-TIME INIT] Completed in {self.init_elapsed:.2f}s — Pipeline is WARM in RAM!\n")

    def synthesize(
        self,
        reference_audio_path: str | Path,
        reference_text: str,
        target_text: str,
        output_wav_path: str | Path,
        audio_format: str = "wav",
        num_steps: int = 8,
        cfg_strength: float = 2.0,
        speed: float = 1.0,
        extra_duration_sec: float = 0.3,
    ) -> dict:
        """
        Clones voice from reference audio to target text, saving to output_wav_path in the requested format.
        """
        start_time = time.time()

        # 1. Load Reference Audio
        y, _ = librosa.load(str(reference_audio_path), sr=SAMPLE_RATE, mono=True)
        audio = self.torch.from_numpy(y).unsqueeze(0).float()
        audio = normalize_audio_rms(audio, target_rms=0.1)

        ref_audio_len = audio.shape[-1] // HOP_LENGTH

        # 2. Syllabic duration estimation (~6.5 mel frames per Indic code point)
        indic_frames_per_char = 6.5 / max(speed, 0.1)
        gen_frames = int(len(target_text.strip()) * indic_frames_per_char)
        extra_pad_frames = int(extra_duration_sec * SAMPLE_RATE / HOP_LENGTH)
        duration = ref_audio_len + gen_frames + extra_pad_frames

        # 3. Clean and format reference text
        clean_ref_text = reference_text.strip()
        if not clean_ref_text.endswith((".", "!", "?", "।")):
            clean_ref_text += "."

        text_list = [clean_ref_text + " " + target_text.strip()]

        ref_duration_sec = ref_audio_len * HOP_LENGTH / SAMPLE_RATE
        target_duration_sec = (duration - ref_audio_len) * HOP_LENGTH / SAMPLE_RATE

        if self.verbose:
            print(f"  ├── Estimated Audio Duration : ~{target_duration_sec:.2f}s ({gen_frames} frames) | Total Window: {duration * HOP_LENGTH / SAMPLE_RATE:.2f}s")
            print(f"  ├── Starting Euler ODE Diffusion ({num_steps} steps, CFG {cfg_strength})...")

        # 4. Continuous Flow Matching sampling
        with self.torch.inference_mode():
            generated, _ = self.model.sample(
                cond=audio,
                text=text_list,
                duration=duration,
                steps=num_steps,
                cfg_strength=cfg_strength,
                sway_sampling_coef=-1.0,
            )
            generated = generated.to(self.torch.float32)
            generated = generated[:, ref_audio_len:, :]

            if self.verbose:
                print("  ├── Decoding mel-spectrogram with Vocos vocoder...")

            # 5. Neural Vocoding to Waveform
            mel = generated.permute(0, 2, 1)
            wav = self.vocoder.decode(mel)
            wav = wav.squeeze().cpu().numpy()

        elapsed = time.time() - start_time
        duration_sec = len(wav) / SAMPLE_RATE
        rtf = elapsed / max(duration_sec, 0.01)

        saved_file = save_audio(output_wav_path, wav, sample_rate=SAMPLE_RATE, fmt=audio_format)

        return {
            "output_path": str(saved_file),
            "elapsed_sec": elapsed,
            "duration_sec": duration_sec,
            "rtf": rtf,
            "sample_rate": SAMPLE_RATE,
        }
