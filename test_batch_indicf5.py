#!/usr/bin/env python3
"""
IndicF5 Batch Voice Cloning Test
Generates multiple audio files sequentially or in parallel from a predefined dictionary/list of prompts.

Usage:
    # 1. Sequential generation (reuses loaded model in memory):
    .\\sherpa-env\\Scripts\\python.exe test_batch_indicf5.py

    # 2. Parallel generation (spawns multiple worker processes):
    .\\sherpa-env\\Scripts\\python.exe test_batch_indicf5.py --parallel --workers 2

    # 3. Custom reference audio & text:
    .\\sherpa-env\\Scripts\\python.exe test_batch_indicf5.py `
      --ref "samples/sudhanva_voic_clone.wav" `
      --ref-text "The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley."
"""

import os
import sys
import codecs
import time
import argparse
from pathlib import Path
from multiprocessing import Process, Queue, cpu_count

# UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Add repo path
REPO_PATH = Path("scratch/indicf5_repo").resolve()
if str(REPO_PATH) not in sys.path:
    sys.path.insert(0, str(REPO_PATH))

# ==============================================
# BATCH PROMPTS CONFIGURATION
# 5 Telugu lines & 5 Tamil lines of varying lengths (Short -> Very Long)
# ==============================================
BATCH_PROMPTS = {
    # ---------------------------------------------------------
    # TELUGU PROMPTS (Varying Lengths)
    # ---------------------------------------------------------
    # 1. Telugu - Short (~4 words, ~2-3s)
    "నమస్కారం, మీరు ఎలా ఉన్నారు?": "generated/sudhanva_telugu_1_short.wav",

    # 2. Telugu - Medium (~8 words, ~4-5s)
    "హలో అందరికీ, ఈ రోజు వాతావరణం చాలా ఆహ్లాదకరంగా ఉంది.": "generated/sudhanva_telugu_2_medium.wav",

    # 3. Telugu - Medium-Long (~14 words, ~7-8s)
    "నేను ఇప్పుడు ఆర్టిఫిషియల్ ఇంటెలిజెన్స్ సహాయంతో మీ స్వరం లో తెలుగు లో మాట్లాడుతున్నాను.": "generated/sudhanva_telugu_3_medlong.wav",

    # 4. Telugu - Long (~20 words, ~10-12s)
    "ఉదయం సూర్యుని లేత కిరణాలు పచ్చని చెట్లపై పడుతుంటే, పక్షుల కిలకిలారావాలతో ప్రకృతి అంతా ఎంతో అందంగా కనిపిస్తుంది.": "generated/sudhanva_telugu_4_long.wav",

    # 5. Telugu - Very Long (~28 words, ~14-16s)
    "మిత్రులారా, సాంకేతిక పరిజ్ఞానం రోజురోజుకు ఎంతో వేగంగా అభివృద్ధి చెందుతోంది. మన స్వంత గొంతును ఇతర భారతీయ భాషల్లోకి సులభంగా మార్చుకునే అవకాశం ఇప్పుడు మనకు లభించింది.": "generated/sudhanva_telugu_5_verylong.wav",

    # ---------------------------------------------------------
    # TAMIL PROMPTS (Varying Lengths)
    # ---------------------------------------------------------
    # 1. Tamil - Short (~4 words, ~2-3s)
    "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?": "generated/sudhanva_tamil_1_short.wav",

    # 2. Tamil - Medium (~8 words, ~4-5s)
    "இன்றைய நாள் உங்கள் அனைவருக்கும் இனிமையாகவும் மகிழ்ச்சியாகவும் அமையட்டும்.": "generated/sudhanva_tamil_2_medium.wav",

    # 3. Tamil - Medium-Long (~13 words, ~7-8s)
    "நான் இப்போது செயற்கை நுண்ணறிவு தொழில்நுட்பத்தின் மூலம் உங்கள் சொந்த குரலில் தமிழில் பேசுகிறேன்.": "generated/sudhanva_tamil_3_medlong.wav",

    # 4. Tamil - Long (~19 words, ~10-12s)
    "காலை நேரத்தில் வீசும் குளிர்ந்த காற்றும், பறவைகளின் இனிய குரல்களும் மனதிற்கு மிகுந்த அமைதியையும் புத்துணர்ச்சியையும் தருகின்றன.": "generated/sudhanva_tamil_4_long.wav",

    # 5. Tamil - Very Long (~26 words, ~14-16s)
    "நண்பர்களே, இன்றைய நவீன அறிவியல் உலகத்தில் பல வியக்கத்தக்க மாற்றங்கள் நிகழ்கின்றன. நமது தாய்மொழியில் நாம் விரும்பும் கருத்துக்களை தொழில்நுட்பத்தின் உதவியுடன் அழகாகப் பகிர முடிகிறது.": "generated/sudhanva_tamil_5_verylong.wav",
}
# ==============================================

# Constants
MODEL_DIR = Path("models/indicf5")
SAFETENSORS_PATH = MODEL_DIR / "model.safetensors"
VOCAB_PATH = MODEL_DIR / "vocab.txt"
SAMPLE_RATE = 24000
HOP_LENGTH = 256


class IndicF5Engine:
    """Encapsulates the loaded IndicF5 CFM + Vocos pipeline for high-performance reuse."""

    def __init__(self):
        import torch
        from safetensors.torch import load_file
        from f5_tts.model.cfm import CFM
        from f5_tts.model.backbones.dit import DiT
        from f5_tts.model.utils import get_tokenizer
        from vocos import Vocos

        self.torch = torch
        print("[Init] Loading IndicF5 Tokenizer & Vocab...")
        vocab_map, vocab_size = get_tokenizer(str(VOCAB_PATH), "custom")

        print("[Init] Instantiating DiT Transformer & CFM...")
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

        print("[Init] Loading Safetensors weights...")
        weights = load_file(str(SAFETENSORS_PATH))
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

        print("[Init] Loading Vocos Vocoder...")
        self.vocoder = Vocos.from_pretrained("charactr/vocos-mel-24khz").eval()
        print("[Init] Engine ready!\n")

    def synthesize(
        self,
        reference_audio_path: str,
        reference_text: str,
        target_text: str,
        output_wav_path: str,
        num_steps: int = 16,
        cfg_strength: float = 2.0,
        speed: float = 1.0,
        extra_duration_sec: float = 0.5,
    ) -> dict:
        import librosa
        import soundfile as sf

        start_time = time.time()

        # 1. Load Reference Audio
        y, sr = librosa.load(reference_audio_path, sr=SAMPLE_RATE, mono=True)
        audio = self.torch.from_numpy(y).unsqueeze(0).float()

        # Normalize audio RMS to standard 0.1 level
        target_rms = 0.1
        rms = self.torch.sqrt(self.torch.mean(self.torch.square(audio)))
        if rms < target_rms and rms.item() > 1e-6:
            audio = audio * (target_rms / rms.item())

        ref_audio_len = audio.shape[-1] // HOP_LENGTH

        # 2. Syllable-based duration estimation (6.5 mel frames per Indic code point)
        indic_frames_per_char = 6.5 / speed
        gen_frames = int(len(target_text.strip()) * indic_frames_per_char)
        extra_pad_frames = int(extra_duration_sec * SAMPLE_RATE / HOP_LENGTH)
        duration = ref_audio_len + gen_frames + extra_pad_frames

        # 3. Clean and format reference text
        clean_ref_text = reference_text.strip()
        if not clean_ref_text.endswith((".", "!", "?", "।")):
            clean_ref_text += "."

        text_list = [clean_ref_text + " " + target_text.strip()]

        # 4. Diffusion sampling
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
            generated_mel_spec = generated.permute(0, 2, 1)
            generated_wave = self.vocoder.decode(generated_mel_spec)
            wav = generated_wave.squeeze().cpu().numpy()

        elapsed = time.time() - start_time
        duration_sec = len(wav) / SAMPLE_RATE

        # 5. Save output file
        out_path = Path(output_wav_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(out_path), wav, samplerate=SAMPLE_RATE, subtype="PCM_16")

        return {
            "output_path": str(out_path),
            "duration_sec": duration_sec,
            "elapsed_sec": elapsed,
            "rtf": elapsed / max(duration_sec, 0.01),
        }


def _worker_process(queue: Queue, result_queue: Queue, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float):
    """Worker process for parallel batch generation."""
    try:
        engine = IndicF5Engine()
        while True:
            item = queue.get()
            if item is None:
                break
            idx, text, out_path = item
            print(f"[Worker PID {os.getpid()}] Processing #{idx+1}: {out_path} ...")
            res = engine.synthesize(
                reference_audio_path=ref_audio,
                reference_text=ref_text,
                target_text=text,
                output_wav_path=out_path,
                num_steps=num_steps,
                cfg_strength=cfg,
                speed=speed,
            )
            result_queue.put((idx, text, res))
    except Exception as e:
        print(f"[Worker Error] {e}")


def run_sequential(prompts_dict: dict, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float):
    """Runs all batch items sequentially using a single model in memory."""
    print("=" * 75)
    print(f" IndicF5 Sequential Batch Processing ({len(prompts_dict)} items)")
    print("=" * 75)
    
    engine = IndicF5Engine()
    results = []

    for i, (text, out_path) in enumerate(prompts_dict.items()):
        print("-" * 75)
        print(f"[{i+1}/{len(prompts_dict)}] Generating -> {out_path}")
        print(f"Text : {text}")
        res = engine.synthesize(
            reference_audio_path=ref_audio,
            reference_text=ref_text,
            target_text=text,
            output_wav_path=out_path,
            num_steps=num_steps,
            cfg_strength=cfg,
            speed=speed,
        )
        print(f"Done in {res['elapsed_sec']:.2f}s (Audio: {res['duration_sec']:.2f}s | RTF: {res['rtf']:.2f}x)")
        results.append((text, res))

    return results


def run_parallel(prompts_dict: dict, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float, workers: int = 2):
    """Runs all batch items across multiple parallel worker processes."""
    print("=" * 75)
    print(f" IndicF5 Parallel Batch Processing ({len(prompts_dict)} items across {workers} workers)")
    print("=" * 75)

    queue = Queue()
    result_queue = Queue()

    items = list(prompts_dict.items())
    for idx, (text, out_path) in enumerate(items):
        queue.put((idx, text, out_path))

    # Send termination sentinels
    for _ in range(workers):
        queue.put(None)

    processes = []
    for _ in range(workers):
        p = Process(
            target=_worker_process,
            args=(queue, result_queue, ref_audio, ref_text, num_steps, cfg, speed),
        )
        p.start()
        processes.append(p)

    results_dict = {}
    for _ in range(len(items)):
        idx, text, res = result_queue.get()
        results_dict[idx] = (text, res)
        print(f"[Completed {len(results_dict)}/{len(items)}] {res['output_path']} ({res['duration_sec']:.2f}s in {res['elapsed_sec']:.2f}s)")

    for p in processes:
        p.join()

    return [results_dict[i] for i in range(len(items))]


def main():
    parser = argparse.ArgumentParser(description="IndicF5 Batch Voice Cloning Test")
    parser.add_argument(
        "--ref",
        type=str,
        default="samples/sudhanva_short_ref.wav",
        help="Path to reference audio file (.wav/.ogg/.mp3)",
    )
    parser.add_argument(
        "--ref-text",
        type=str,
        default="The quick brown fox jumps over the lazy dog.",
        help="Transcript of reference audio",
    )
    parser.add_argument(
        "--parallel",
        "-p",
        action="store_true",
        help="Run batch items in parallel across multiple worker processes",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=2,
        help="Number of worker processes when running in parallel (default: 2)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=8,
        help="Diffusion steps (default: 8)",
    )
    parser.add_argument(
        "--cfg",
        type=float,
        default=2.0,
        help="Classifier-Free Guidance strength (default: 2.0)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed multiplier (default: 1.0)",
    )
    args = parser.parse_args()

    overall_start = time.time()

    if args.parallel:
        results = run_parallel(
            prompts_dict=BATCH_PROMPTS,
            ref_audio=args.ref,
            ref_text=args.ref_text,
            num_steps=args.steps,
            cfg=args.cfg,
            speed=args.speed,
            workers=args.workers,
        )
    else:
        results = run_sequential(
            prompts_dict=BATCH_PROMPTS,
            ref_audio=args.ref,
            ref_text=args.ref_text,
            num_steps=args.steps,
            cfg=args.cfg,
            speed=args.speed,
        )

    overall_time = time.time() - overall_start

    # Final summary table
    print("\n" + "=" * 85)
    print(f" BATCH GENERATION COMPLETED ({len(results)} files in {overall_time:.2f}s)")
    print("=" * 85)
    print(f"{'#':<3} | {'Output File':<35} | {'Audio Len':<10} | {'Gen Time':<10} | {'RTF':<8}")
    print("-" * 85)
    for i, (text, res) in enumerate(results):
        print(f"{i+1:<3} | {res['output_path']:<35} | {res['duration_sec']:>7.2f} s | {res['elapsed_sec']:>7.2f} s | {res['rtf']:>6.2f}x")
    print("=" * 85)


if __name__ == "__main__":
    main()
