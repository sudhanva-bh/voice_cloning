#!/usr/bin/env python3
"""
IndicF5 High-Fidelity Batch Voice Cloning Engine
Demonstrates one-time cold initialization in memory followed by fast back-to-back synthesis.
Automatically increments output directories to generated/batches/batch-1, batch-2, etc.

Usage:
    # Sequential batch generation (Model loaded once into RAM, reused across all prompts):
    .\\sherpa-env\\Scripts\\python.exe test_batch_indicf5.py `
      --ref "samples/sudhanva_short_ref.wav" `
      --ref-text "The quick brown fox jumps over the lazy dog." `
      --steps 8

    # Using native Tamil reference:
    .\\sherpa-env\\Scripts\\python.exe test_batch_indicf5.py `
      --ref "samples/tamil_voices/tamil1.mp3" `
      --ref-text "யாதும் ஊரே யாவரும் கேளிர் என்ற உயரிய சிந்தனை, உலகெங்கும் வாழும் மனிதர்களின் இதயங்களில் அன்பையும் அமைதியையும் விதைக்கட்டும்." `
      --steps 8
"""

import os
import sys
import codecs
import time
import argparse
from datetime import datetime
from pathlib import Path
from multiprocessing import Process, Queue, cpu_count

# Force unbuffered UTF-8 stdout and stderr for instant real-time printing
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True, write_through=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True, write_through=True)
    except AttributeError:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Override built-in print to ALWAYS flush immediately
_orig_print = print
def print(*args, **kwargs):
    kwargs.setdefault("flush", True)
    _orig_print(*args, **kwargs)

# Add repo path
REPO_PATH = Path("scratch/indicf5_repo").resolve()
if str(REPO_PATH) not in sys.path:
    sys.path.insert(0, str(REPO_PATH))

# ==============================================
# BATCH PROMPTS CONFIGURATION
# 3 Telugu and 3 Tamil prompts ranging from 4 to 12 seconds (Medium-Long -> Very Long)
# ==============================================
BATCH_PROMPTS = {
    # ---------------------------------------------------------
    # TELUGU PROMPTS (4s to 12s)
    # ---------------------------------------------------------
    # 1. Telugu - Medium-Long (~5.5s, ~75 chars)
    "నేను ఇప్పుడు ఆర్టిఫిషియల్ ఇంటెలిజెన్స్ సహాయంతో మీ స్వంత గొంతుతో తెలుగులో మాట్లాడుతున్నాను.": "telugu_1_medlong.wav",

    # 2. Telugu - Long (~8.5s, ~115 chars)
    "ఉదయం సూర్యుని లేత కిరణాలు పచ్చని చెట్లపై పడుతుంటే, పక్షుల కిలకిలారావాలతో ప్రకృతి అంతా ఎంతో అందంగా కనిపిస్తుంది.": "telugu_2_long.wav",

    # 3. Telugu - Very Long (~11.5s, ~155 chars)
    "మిత్రులారా, సాంకేతిక పరిజ్ఞానం రోజురోజుకు ఎంతో వేగంగా అభివృద్ధి చెందుతోంది. మన స్వంత గొంతును ఇతర భారతీయ భాషల్లోకి సులభంగా మార్చుకునే అవకాశం ఇప్పుడు మనకు లభించింది.": "telugu_3_verylong.wav",

    # ---------------------------------------------------------
    # TAMIL PROMPTS (4s to 12s)
    # ---------------------------------------------------------
    # 1. Tamil - Medium-Long (~5.5s, ~75 chars)
    "நான் இப்போது செயற்கை நுண்ணறிவு தொழில்நுட்பத்தின் மூலம் உங்கள் சொந்த குரலில் தமிழில் பேசுகிறேன்.": "tamil_1_medlong.wav",

    # 2. Tamil - Long (~8.5s, ~115 chars)
    "காலை நேரத்தில் வீசும் குளிர்ந்த காற்றும், பறவைகளின் இனிய குரல்களும் மனதிற்கு மிகுந்த அமைதியையும் புத்துணர்ச்சியையும் தருகின்றன.": "tamil_2_long.wav",

    # 3. Tamil - Very Long (~11.5s, ~155 chars)
    "நண்பர்களே, இன்றைய நவீன அறிவியல் உலகத்தில் பல வியக்கத்தக்க மாற்றங்கள் நிகழ்கின்றன. நமது தாய்மொழியில் நாம் விரும்பும் கருத்துக்களை தொழில்நுட்பத்தின் உதவியுடன் அழகாகப் பகிர முடிகிறது.": "tamil_3_verylong.wav",
}
# ==============================================

# Constants
MODEL_DIR = Path("models/indicf5")
SAFETENSORS_PATH = MODEL_DIR / "model.safetensors"
VOCAB_PATH = MODEL_DIR / "vocab.txt"
SAMPLE_RATE = 24000
HOP_LENGTH = 256


def get_next_batch_dir(base_dir: Path = Path("generated/batches")) -> Path:
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


class IndicF5Engine:
    """Encapsulates the loaded IndicF5 CFM + Vocos pipeline for high-performance memory reuse."""

    def __init__(self):
        import torch
        from safetensors.torch import load_file
        from f5_tts.model.cfm import CFM
        from f5_tts.model.backbones.dit import DiT
        from f5_tts.model.utils import get_tokenizer
        from vocos import Vocos

        self.torch = torch
        init_start = time.time()
        print("  ├── [1/4] Loading Tokenizer & Vocabulary (vocab.txt)...")
        vocab_map, vocab_size = get_tokenizer(str(VOCAB_PATH), "custom")

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

        print("  ├── [3/4] Reading & parsing 1.35 GB Safetensors weights into RAM...")
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

        print("  └── [4/4] Loading Vocos 24kHz Neural Vocoder...")
        self.vocoder = Vocos.from_pretrained("charactr/vocos-mel-24khz").eval()
        self.init_elapsed = time.time() - init_start
        print(f" [ONE-TIME INIT] Completed in {self.init_elapsed:.2f}s — Pipeline is WARM in RAM!\n")

    def synthesize(
        self,
        reference_audio_path: str,
        reference_text: str,
        target_text: str,
        output_wav_path: str,
        num_steps: int = 8,
        cfg_strength: float = 2.0,
        speed: float = 1.0,
        extra_duration_sec: float = 0.3,
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

        ref_duration_sec = ref_audio_len * HOP_LENGTH / SAMPLE_RATE
        target_duration_sec = (duration - ref_audio_len) * HOP_LENGTH / SAMPLE_RATE

        print(f"  ├── Estimated Audio Duration : ~{target_duration_sec:.2f}s ({gen_frames} frames) | Total Window: {duration * HOP_LENGTH / SAMPLE_RATE:.2f}s")
        print(f"  ├── Starting Euler ODE Diffusion ({num_steps} steps, CFG {cfg_strength})...")

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

            print("  ├── Decoding mel-spectrogram with Vocos vocoder...")
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
            "char_count": len(target_text.strip()),
            "ref_sec": ref_duration_sec,
            "target_sec": target_duration_sec,
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
            print(f"[Worker PID {os.getpid()}] STARTING #{idx+1}: {out_path}")
            res = engine.synthesize(
                reference_audio_path=ref_audio,
                reference_text=ref_text,
                target_text=text,
                output_wav_path=out_path,
                num_steps=num_steps,
                cfg_strength=cfg,
                speed=speed,
            )
            print(f"[Worker PID {os.getpid()}] FINISHED #{idx+1}: {out_path} ({res['duration_sec']:.2f}s in {res['elapsed_sec']:.2f}s)")
            result_queue.put((idx, text, res))
    except Exception as e:
        print(f"[Worker Error] {e}")


def run_sequential(prompts_dict: dict, batch_dir: Path, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float):
    """Runs all batch items sequentially using a single model kept warm in memory."""
    print("=" * 80)
    print(" [Start Batch Script] IndicF5 High-Fidelity Batch Synthesis (Sequential)")
    print("=" * 80)
    print(f" Output Folder   : {batch_dir.resolve()}")
    print(f" Reference Audio : {ref_audio}")
    print(f" Reference Text  : {ref_text}")
    print(f" Total Prompts   : {len(prompts_dict)} items")
    print(f" Diffusion Steps : {num_steps} (CFG: {cfg})")
    print(f" Duration Rate   : {6.5/speed:.1f} mel frames / char")
    print("-" * 80)
    print(" [ONE-TIME INIT] Loading IndicF5 Pipeline into RAM (happens only once)...")
    
    engine = IndicF5Engine()
    results = []

    for i, (text, out_path) in enumerate(prompts_dict.items()):
        now_time = datetime.now().strftime("%H:%M:%S")
        print(f" [{i+1}/{len(prompts_dict)}] STARTING [{now_time}] -> {out_path}")
        print(f"  ├── Target Text              : \"{text}\" ({len(text)} chars)")
        
        res = engine.synthesize(
            reference_audio_path=ref_audio,
            reference_text=ref_text,
            target_text=text,
            output_wav_path=out_path,
            num_steps=num_steps,
            cfg_strength=cfg,
            speed=speed,
        )
        print(f"  └── FINISHED in {res['elapsed_sec']:.2f}s | Audio: {res['duration_sec']:.2f}s | Speed: {res['rtf']:.2f}x RTF -> Saved to {out_path}\n")
        results.append((text, res))

    return results, engine.init_elapsed


def run_parallel(prompts_dict: dict, batch_dir: Path, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float, workers: int = 2):
    """Runs all batch items across multiple parallel worker processes."""
    print("=" * 80)
    print(f" [Start Batch Script] IndicF5 Parallel Batch Synthesis ({workers} Workers)")
    print("=" * 80)
    print(f" Output Folder   : {batch_dir.resolve()}")
    print(f" Reference Audio : {ref_audio}")
    print(f" Reference Text  : {ref_text}")
    print(f" Total Prompts   : {len(prompts_dict)} items across {workers} parallel processes")
    print("-" * 80)

    queue = Queue()
    result_queue = Queue()

    items = list(prompts_dict.items())
    for idx, (text, out_path) in enumerate(items):
        queue.put((idx, text, out_path))

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

    for p in processes:
        p.join()

    return [results_dict[i] for i in range(len(items))], 0.0


def main():
    parser = argparse.ArgumentParser(description="IndicF5 Batch Voice Cloning Engine")
    parser.add_argument(
        "--ref",
        type=str,
        default="samples/sudhanva_short_ref.wav",
        help="Path to reference audio file (.wav/.mp3/.ogg)",
    )
    parser.add_argument(
        "--ref-text",
        type=str,
        default="The quick brown fox jumps over the lazy dog.",
        help="Transcript of the reference audio",
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

    # Automatically allocate next batch directory: generated/batches/batch-1, batch-2, etc.
    batch_dir = get_next_batch_dir()
    prompts_with_paths = {
        text: str(batch_dir / filename)
        for text, filename in BATCH_PROMPTS.items()
    }

    overall_start = time.time()

    if args.parallel:
        results, init_time = run_parallel(
            prompts_dict=prompts_with_paths,
            batch_dir=batch_dir,
            ref_audio=args.ref,
            ref_text=args.ref_text,
            num_steps=args.steps,
            cfg=args.cfg,
            speed=args.speed,
            workers=args.workers,
        )
    else:
        results, init_time = run_sequential(
            prompts_dict=prompts_with_paths,
            batch_dir=batch_dir,
            ref_audio=args.ref,
            ref_text=args.ref_text,
            num_steps=args.steps,
            cfg=args.cfg,
            speed=args.speed,
        )

    overall_time = time.time() - overall_start
    total_audio_sec = sum(res["duration_sec"] for _, res in results)
    total_synth_sec = sum(res["elapsed_sec"] for _, res in results)
    avg_rtf = total_synth_sec / max(total_audio_sec, 0.01)

    # Final Summary Table
    print("=" * 85)
    print(f" [Batch Completed] Batch Synthesis Summary ({len(results)} files in {overall_time:.2f}s)")
    print(f" Output Folder : {batch_dir.resolve()}")
    print("=" * 85)
    print(f"{'#':<3} | {'Output File':<42} | {'Audio Len':<10} | {'Gen Time':<10} | {'RTF':<8}")
    print("-" * 85)
    for i, (text, res) in enumerate(results):
        rel_path = Path(res['output_path']).name
        print(f"{i+1:<3} | {rel_path:<42} | {res['duration_sec']:>7.2f} s | {res['elapsed_sec']:>7.2f} s | {res['rtf']:>6.2f}x")
    print("-" * 85)
    print(f" Total Audio Generated : {total_audio_sec:.2f} seconds")
    print(f" Total Generation Time : {total_synth_sec:.2f} seconds (Avg Speed: {avg_rtf:.2f}x RTF)")
    if init_time > 0:
        saved_io_time = (len(results) - 1) * init_time
        print(f" One-Time Cold Load    : {init_time:.2f}s (Saved ~{saved_io_time:.2f}s of redundant 1.35GB disk I/O!)")
    print("=" * 85)


if __name__ == "__main__":
    main()
