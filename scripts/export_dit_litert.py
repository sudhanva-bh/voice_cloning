#!/usr/bin/env python3
"""
IndicF5 Diffusion Transformer (DiT) Export Script for Google LiteRT.
Loads pretrained model.safetensors weights, wraps the DiT backbone for static inference,
and exports an optimized .tflite FlatBuffer for on-device voice generation.
"""

import argparse
import gc
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

# Add indicf5 repo to python path
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRATCH_REPO = REPO_ROOT / "scratch" / "indicf5_repo"
if SCRATCH_REPO.is_dir():
    sys.path.insert(0, str(SCRATCH_REPO))

# Import LiteRT compiler
try:
    import litert_torch
except ImportError:
    try:
        import ai_edge_torch as litert_torch
    except ImportError:
        print("[ERROR] Neither litert_torch nor ai_edge_torch is installed.")
        sys.exit(1)

from safetensors.torch import load_file
from f5_tts.model.backbones.dit import DiT


class IndicF5DiTExportWrapper(torch.nn.Module):
    """
    Inference wrapper for IndicF5 DiT that freezes train-time dropout flags
    (drop_audio_cond=False, drop_text=False, mask=None) into constants,
    enabling deterministic TorchDynamo graph capture and MLIR lowering.
    """
    def __init__(self, dit_model: DiT):
        super().__init__()
        self.dit = dit_model

    def forward(
        self,
        x: torch.Tensor,
        cond: torch.Tensor,
        text: torch.Tensor,
        t: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            x:    [1, seq_len, 100] float32 noised mel state
            cond: [1, seq_len, 100] float32 reference audio conditioning
            text: [1, text_len]     int32 token IDs
            t:    [1]               float32 continuous diffusion time step
        Returns:
            v_pred: [1, seq_len, 100] float32 predicted velocity field
        """
        return self.dit(
            x=x,
            cond=cond,
            text=text,
            time=t,
            drop_audio_cond=False,
            drop_text=False,
            mask=None,
        )


def export_dit(
    checkpoint_path: Path,
    vocab_path: Path,
    output_path: Path,
    seq_len: int = 512,
    text_len: int = 128,
):
    print("=" * 78)
    print("        GOOGLE LITERt EXPORT — INDICF5 DIFFUSION TRANSFORMER (FP32)")
    print("=" * 78)
    print(f"Checkpoint:      {checkpoint_path}")
    print(f"Vocab File:      {vocab_path}")
    print(f"Target Output:   {output_path}")
    print(f"Sequence Length: {seq_len} frames (~{seq_len * 256 / 24000:.2f} seconds)")
    print(f"Text Length:     {text_len} tokens")

    # 1. Determine vocab size
    print("\n[Step 1/5] Reading vocab file to determine embedding vocabulary size...")
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab_size = len(f.readlines())
    print(f"  Vocab Size: {vocab_size} tokens")

    # 2. Instantiate DiT architecture
    print("\n[Step 2/5] Instantiating 335M-parameter DiT architecture...")
    model_cfg = dict(
        dim=1024,
        depth=22,
        heads=16,
        ff_mult=2,
        text_dim=512,
        conv_layers=4,
        text_num_embeds=vocab_size,
        mel_dim=100,
    )
    dit = DiT(**model_cfg).eval()

    # 3. Load safetensors weights
    print("\n[Step 3/5] Loading weights from model.safetensors...")
    ckpt = load_file(str(checkpoint_path))
    dit_state_dict = {
        k.replace("transformer.", "").replace("ema_model.", ""): v
        for k, v in ckpt.items()
        if "transformer." in k
    }
    msg = dit.load_state_dict(dit_state_dict, strict=True)
    print(f"  [PASSED] Strict weight loading verified: {msg}")
    del ckpt, dit_state_dict
    gc.collect()

    wrapped_dit = IndicF5DiTExportWrapper(dit).eval()

    # 4. LiteRT compilation
    print("\n[Step 4/5] Tracing and converting to Google LiteRT FlatBuffer...")
    dummy_x = torch.zeros(1, seq_len, 100, dtype=torch.float32)
    dummy_cond = torch.zeros(1, seq_len, 100, dtype=torch.float32)
    dummy_text = torch.zeros(1, text_len, dtype=torch.int32)
    dummy_t = torch.tensor([0.5], dtype=torch.float32)

    sample_inputs = (dummy_x, dummy_cond, dummy_text, dummy_t)

    t0 = time.time()
    edge_model = litert_torch.convert(wrapped_dit, sample_inputs)
    compile_time = time.time() - t0
    print(f"  [PASSED] Compilation completed in {compile_time:.1f} seconds")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    edge_model.export(str(output_path))
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  [PASSED] Serialized FlatBuffer: {output_path} ({file_size_mb:.2f} MB)")

    # 5. Runtime verification with XNNPACK
    print("\n[Step 5/5] Verifying LiteRT runtime interpreter with XNNPACK...")
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        try:
            from litert.interpreter import Interpreter
        except ImportError:
            from tflite_runtime.interpreter import Interpreter

    interp = Interpreter(model_path=str(output_path))
    interp.allocate_tensors()
    in_details = interp.get_input_details()
    out_details = interp.get_output_details()

    print("  Model Input Signatures:")
    for d in in_details:
        print(f"    - {d['name']}: shape {d['shape']}, dtype {d['dtype']}")

    print("  Model Output Signatures:")
    for d in out_details:
        print(f"    - {d['name']}: shape {d['shape']}, dtype {d['dtype']}")

    # Set dummy values
    for d in in_details:
        val = np.zeros(d["shape"], dtype=d["dtype"])
        interp.set_tensor(d["index"], val)

    t_inv0 = time.time()
    interp.invoke()
    inv_time = time.time() - t_inv0
    out_tensor = interp.get_tensor(out_details[0]["index"])

    print(f"  Inference Test Passed in {inv_time:.2f}s | Output Shape: {out_tensor.shape}")
    print(f"  Output Min/Max: [{out_tensor.min():.4f}, {out_tensor.max():.4f}]")
    assert not np.isnan(out_tensor).any(), "Output contains NaN values!"
    print("  [PASSED] LiteRT XNNPACK interpreter executed with finite output.")

    print("\n" + "=" * 78)
    print("  🎉 INDICF5 DIT LITERt FP32 EXPORT COMPLETE!")
    print("=" * 78 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Export IndicF5 DiT to LiteRT FP32 FlatBuffer")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="/mnt/c/voice_cloning/models/indicf5/model.safetensors",
        help="Path to model.safetensors",
    )
    parser.add_argument(
        "--vocab",
        type=str,
        default="/mnt/c/voice_cloning/models/indicf5/vocab.txt",
        help="Path to vocab.txt",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/mnt/c/voice_cloning/models/indicf5/indicf5_dit_fp32.tflite",
        help="Path to output .tflite file",
    )
    parser.add_argument(
        "--seq_len",
        type=int,
        default=512,
        help="Fixed sequence length in mel frames (default: 512 ~ 5.46 sec)",
    )
    parser.add_argument(
        "--text_len",
        type=int,
        default=128,
        help="Fixed text sequence length in token count (default: 128)",
    )
    args = parser.parse_args()
    export_dit(
        Path(args.checkpoint),
        Path(args.vocab),
        Path(args.output),
        seq_len=args.seq_len,
        text_len=args.text_len,
    )


if __name__ == "__main__":
    main()
