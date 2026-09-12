#!/usr/bin/env python3
"""
IndicF5 High-Fidelity Batch Voice Cloning Engine
Demonstrates one-time cold initialization in memory followed by fast back-to-back synthesis.
Automatically increments output directories to generated/batches/batch-1, batch-2, etc.

Usage:
    # 1. Using a preset voice key from voices.json (Recommended):
    .\\sherpa-env\\Scripts\\python.exe test_batch_indicf5.py `
      --voice deep_classic `
      --steps 8

    # 2. List all available preset voice keys:
    .\\sherpa-env\\Scripts\\python.exe test_batch_indicf5.py --list-voices

    # 3. Using direct reference audio & transcript:
    .\\sherpa-env\\Scripts\\python.exe test_batch_indicf5.py `
      --ref "samples/sudhanva_short_ref.wav" `
      --ref-text "The quick brown fox jumps over the lazy dog." `
      --steps 8
"""

import os
import sys
import json
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
# PROMPTS DATASET LOADER WITH MULTI-SELECT
# ==============================================
PROMPTS_JSON_PATH = Path("prompts.json")

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
    """Parses space-separated, comma-separated, range, or number/keyword tokens (e.g. '1 2', '2-4', '1-3', 'telugu, tamil')."""
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
    """Parses count integer, space-separated indices ('1 2', '1 2 3', '2 3 4'), ranges ('1-4'), or 'all'/'0'."""
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


def load_prompts_from_json(
    prompts_file: str = "prompts.json",
    languages="all",
    categories="all",
    count_per_category=1,
    audio_format: str = "wav",
) -> dict:
    """Loads customizable phrase dictionary from prompts.json supporting multi-select numbers/keywords."""
    path = Path(prompts_file)
    if not path.is_file():
        alt = Path("data/prompts.json")
        if alt.is_file():
            path = alt
        else:
            raise FileNotFoundError(f"Prompts dataset file not found at: {prompts_file}")
            
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    default_langs = ["telugu", "tamil", "hindi"]
    default_cats = ["short", "medium", "midlong", "long"]
    
    req_langs = parse_multi_selection(languages, LANG_MAP, default_langs)
    req_cats = parse_multi_selection(categories, TIER_MAP, default_cats)
    
    ext = audio_format.lower().replace(".", "")
    selected_prompts = {}
    
    for lang in req_langs:
        lang_data = data.get(lang, {})
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


def save_audio(out_path: str, wav, sample_rate: int = SAMPLE_RATE, fmt: str = "wav") -> Path:
    import soundfile as sf
    path = Path(out_path)
    if fmt and fmt.lower() in ("wav", "mp3", "ogg", "flac"):
        if path.suffix.lower().replace(".", "") != fmt.lower():
            path = path.with_suffix(f".{fmt.lower()}")
    ext = path.suffix.lower().replace(".", "")
    path.parent.mkdir(parents=True, exist_ok=True)
    if ext == "mp3":
        sf.write(str(path), wav, samplerate=sample_rate, format="MP3")
    elif ext in ("ogg", "oga"):
        sf.write(str(path), wav, samplerate=sample_rate, format="OGG")
    elif ext == "flac":
        sf.write(str(path), wav, samplerate=sample_rate, format="FLAC")
    else:
        sf.write(str(path), wav, samplerate=sample_rate, subtype="PCM_16")
    return path


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
        audio_format: str = "wav",
        num_steps: int = 8,
        cfg_strength: float = 2.0,
        speed: float = 1.0,
        extra_duration_sec: float = 0.3,
    ) -> dict:
        import librosa

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
        saved_path = save_audio(output_wav_path, wav, sample_rate=SAMPLE_RATE, fmt=audio_format)

        return {
            "output_path": str(saved_path),
            "char_count": len(target_text.strip()),
            "ref_sec": ref_duration_sec,
            "target_sec": target_duration_sec,
            "duration_sec": duration_sec,
            "elapsed_sec": elapsed,
            "rtf": elapsed / max(duration_sec, 0.01),
        }


def _worker_process(queue: Queue, result_queue: Queue, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float, audio_format: str = "wav"):
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
                audio_format=audio_format,
                num_steps=num_steps,
                cfg_strength=cfg,
                speed=speed,
            )
            print(f"[Worker PID {os.getpid()}] FINISHED #{idx+1}: {out_path} ({res['duration_sec']:.2f}s in {res['elapsed_sec']:.2f}s)")
            result_queue.put((idx, text, res))
    except Exception as e:
        print(f"[Worker Error] {e}")


def run_sequential(prompts_dict: dict, batch_dir: Path, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float, audio_format: str = "wav"):
    """Runs all batch items sequentially using a single model kept warm in memory."""
    print("=" * 80)
    print(" [Start Batch Script] IndicF5 High-Fidelity Batch Synthesis (Sequential)")
    print("=" * 80)
    print(f" Output Folder   : {batch_dir.resolve()}")
    print(f" Output Format   : {audio_format.upper()}")
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
            audio_format=audio_format,
            num_steps=num_steps,
            cfg_strength=cfg,
            speed=speed,
        )
        print(f"  └── FINISHED in {res['elapsed_sec']:.2f}s | Audio: {res['duration_sec']:.2f}s | Speed: {res['rtf']:.2f}x RTF -> Saved to {out_path}\n")
        results.append((text, res))

    return results, engine.init_elapsed


def run_parallel(prompts_dict: dict, batch_dir: Path, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float, audio_format: str = "wav", workers: int = 2):
    """Runs all batch items across multiple parallel worker processes."""
    print("=" * 80)
    print(f" [Start Batch Script] IndicF5 Parallel Batch Synthesis ({workers} Workers)")
    print("=" * 80)
    print(f" Output Folder   : {batch_dir.resolve()}")
    print(f" Output Format   : {audio_format.upper()}")
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
            args=(queue, result_queue, ref_audio, ref_text, num_steps, cfg, speed, audio_format),
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


def load_voice_from_json(voice_key: str, json_path: str = "samples/voices.json"):
    path = Path(json_path)
    if not path.is_file():
        # Fallback check
        alt_json = Path("samples/tamil_voices/voices.json")
        if alt_json.is_file():
            path = alt_json
        else:
            raise FileNotFoundError(f"Voices JSON mapping file not found at: {json_path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if voice_key not in data:
        available = "\n  - " + "\n  - ".join(data.keys())
        raise KeyError(f"Voice key '{voice_key}' not found in {path}. Available keys:{available}")
    entry = data[voice_key]
    audio_path = entry["audio"]
    
    # Resolve audio path robustly
    audio_p = Path(audio_path)
    if not audio_p.is_file():
        candidates = [
            path.parent / audio_path,
            path.parent / audio_p.name,
            Path("samples") / audio_path,
            Path("samples/added") / audio_p.name,
            Path("samples/tamil_voices") / audio_p.name,
        ]
        for c in candidates:
            if c.is_file():
                audio_path = str(c)
                break
    return audio_path, entry["transcript"]


def main():
    parser = argparse.ArgumentParser(description="IndicF5 Batch Voice Cloning Engine")
    parser.add_argument(
        "--voice",
        "--voice-key",
        type=str,
        default=None,
        help="Preset voice key from voices.json (e.g. tamil_classic_pangram, deep_classic, sudhanva_english)",
    )
    parser.add_argument(
        "--voices-json",
        type=str,
        default="samples/voices.json",
        help="Path to voices.json mapping file (default: samples/voices.json)",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available preset voice keys from voices.json and exit",
    )
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
        "--prompts-file",
        type=str,
        default="prompts.json",
        help="Path to prompts dataset JSON file (default: prompts.json)",
    )
    parser.add_argument(
        "--lang",
        "--language",
        type=str,
        default="all",
        help="Language filter: 'all', or comma-separated list like 'telugu', 'tamil', 'hindi', 'telugu,tamil' (default: all)",
    )
    parser.add_argument(
        "--tier",
        "--length",
        type=str,
        default="all",
        help="Length tier filter: 'all', or comma-separated list like 'short', 'medium', 'midlong', 'long' (default: all)",
    )
    parser.add_argument(
        "--count",
        "--limit",
        type=str,
        default="1",
        help="Number of phrases or specific indices per category tier (e.g. '1', '2', '1 2', '2 3 4', '1-4', or '0' for all 10)",
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List available phrases in the prompts JSON file and exit",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        default="wav",
        choices=["wav", "mp3", "ogg", "flac"],
        help="Output audio format: wav, mp3, ogg, or flac (default: wav)",
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

    # If listing prompts, display available sentences and exit
    if args.list_prompts:
        prompts_path = Path(args.prompts_file)
        if not prompts_path.is_file():
            print(f"Prompts file not found at: {prompts_path}")
            sys.exit(1)
        with open(prompts_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("=" * 85)
        print(f" 📖 Available Batch Phrases in {prompts_path.resolve()}")
        print("=" * 85)
        for lang, tiers in data.items():
            print(f"\n Language: {lang.upper()}")
            for tier, sentences in tiers.items():
                print(f"  [{tier.upper()}] ({len(sentences)} phrases):")
                for s_idx, s in enumerate(sentences):
                    print(f"    {s_idx+1}. {s}")
        print("=" * 85)
        sys.exit(0)

    # If listing voices, display available keys and exit
    if args.list_voices:
        json_path = Path(args.voices_json)
        if not json_path.is_file():
            print(f"Voices JSON file not found at: {json_path}")
            sys.exit(1)
        with open(json_path, "r", encoding="utf-8") as f:
            voices = json.load(f)
        print("=" * 70)
        print(f" Available Voice Keys in {json_path.resolve()}")
        print("=" * 70)
        for key, info in voices.items():
            print(f" Key   : {key}")
            print(f" Audio : {info.get('audio')}")
            print(f" Desc  : {info.get('description', '')}")
            print(f" Text  : {info.get('transcript')}")
            print("-" * 70)
        sys.exit(0)

    ref_audio = args.ref
    ref_text = args.ref_text

    # Resolve from voices.json if voice key is specified
    if args.voice:
        ref_audio, ref_text = load_voice_from_json(args.voice, args.voices_json)
        print(f"[Preset Voice] Loaded voice '{args.voice}' from {args.voices_json}")

    # Load filtered prompts from prompts.json
    selected_prompts = load_prompts_from_json(
        prompts_file=args.prompts_file,
        languages=args.lang,
        categories=args.tier,
        count_per_category=args.count,
        audio_format=args.format,
    )

    if not selected_prompts:
        print(f"[Error] No phrases matched filter: lang='{args.lang}', tier='{args.tier}' in {args.prompts_file}")
        sys.exit(1)

    # Automatically allocate next batch directory: generated/batches/batch-1, batch-2, etc.
    batch_dir = get_next_batch_dir()
    prompts_with_paths = {
        text: str(batch_dir / filename)
        for text, filename in selected_prompts.items()
    }

    overall_start = time.time()

    if args.parallel:
        results, init_time = run_parallel(
            prompts_dict=prompts_with_paths,
            batch_dir=batch_dir,
            ref_audio=ref_audio,
            ref_text=ref_text,
            num_steps=args.steps,
            cfg=args.cfg,
            speed=args.speed,
            audio_format=args.format,
            workers=args.workers,
        )
    else:
        results, init_time = run_sequential(
            prompts_dict=prompts_with_paths,
            batch_dir=batch_dir,
            ref_audio=ref_audio,
            ref_text=ref_text,
            num_steps=args.steps,
            cfg=args.cfg,
            speed=args.speed,
            audio_format=args.format,
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
