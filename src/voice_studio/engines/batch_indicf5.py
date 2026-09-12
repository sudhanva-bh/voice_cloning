"""
IndicF5 Batch synthesis runner supporting sequential memory reuse and multiprocessing workers.
"""

import os
import time
from pathlib import Path
from datetime import datetime
from multiprocessing import Process, Queue, cpu_count

from ..config import BATCHES_DIR
from .indicf5 import IndicF5Engine


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


def _worker_process(queue: Queue, result_queue: Queue, ref_audio: str, ref_text: str, num_steps: int, cfg: float, speed: float, audio_format: str):
    """Worker process for parallel batch generation."""
    try:
        engine = IndicF5Engine(verbose=False)
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


class IndicF5BatchRunner:
    """Orchestrates batch voice synthesis with single model warm load or multi-worker execution."""

    def __init__(self, engine: IndicF5Engine | None = None):
        self.engine = engine

    def run_sequential(
        self,
        prompts_dict: dict[str, str],
        batch_dir: Path,
        ref_audio: str,
        ref_text: str,
        num_steps: int = 8,
        cfg: float = 2.0,
        speed: float = 1.0,
        audio_format: str = "wav",
    ) -> tuple[list[tuple[str, dict]], float]:
        """Runs batch sequentially reusing the warm in-memory model."""
        print("=" * 80)
        print(" [Start Batch Script] IndicF5 High-Fidelity Batch Synthesis (Sequential)")
        print("=" * 80)
        print(f" Output Folder   : {batch_dir.resolve()}")
        print(f" Output Format   : {audio_format.upper()}")
        print(f" Reference Audio : {ref_audio}")
        print(f" Reference Text  : {ref_text}")
        print(f" Total Prompts   : {len(prompts_dict)} items")
        print(f" Diffusion Steps : {num_steps} (CFG: {cfg})")
        print(f" Duration Rate   : {6.5/max(speed, 0.1):.1f} mel frames / char")
        print("-" * 80)
        print(" [ONE-TIME INIT] Loading IndicF5 Pipeline into RAM (happens only once)...")

        init_time = 0.0
        if self.engine is None:
            self.engine = IndicF5Engine()
            init_time = self.engine.init_elapsed

        results = []
        for i, (text, out_path) in enumerate(prompts_dict.items()):
            now_time = datetime.now().strftime("%H:%M:%S")
            print(f" [{i+1}/{len(prompts_dict)}] STARTING [{now_time}] -> {out_path}")
            print(f"  ├── Target Text              : \"{text}\" ({len(text)} chars)")

            res = self.engine.synthesize(
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

        return results, init_time

    def run_parallel(
        self,
        prompts_dict: dict[str, str],
        batch_dir: Path,
        ref_audio: str,
        ref_text: str,
        num_steps: int = 8,
        cfg: float = 2.0,
        speed: float = 1.0,
        audio_format: str = "wav",
        workers: int = 2,
    ) -> tuple[list[tuple[str, dict]], float]:
        """Runs batch items in parallel across multiple worker processes."""
        num_workers = min(workers, cpu_count(), len(prompts_dict))
        print("=" * 80)
        print(f" [Start Batch Script] IndicF5 High-Fidelity Batch Synthesis (Parallel: {num_workers} Workers)")
        print("=" * 80)
        print(f" Output Folder   : {batch_dir.resolve()}")
        print(f" Output Format   : {audio_format.upper()}")
        print(f" Reference Audio : {ref_audio}")
        print(f" Total Prompts   : {len(prompts_dict)} items")
        print("-" * 80)

        queue = Queue()
        result_queue = Queue()

        for idx, (text, out_path) in enumerate(prompts_dict.items()):
            queue.put((idx, text, out_path))
        for _ in range(num_workers):
            queue.put(None)

        processes = []
        for _ in range(num_workers):
            p = Process(
                target=_worker_process,
                args=(queue, result_queue, ref_audio, ref_text, num_steps, cfg, speed, audio_format),
            )
            p.start()
            processes.append(p)

        results_indexed = []
        for _ in range(len(prompts_dict)):
            results_indexed.append(result_queue.get())

        for p in processes:
            p.join()

        results_indexed.sort(key=lambda x: x[0])
        results = [(text, res) for _, text, res in results_indexed]
        return results, 0.0
