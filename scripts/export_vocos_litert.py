#!/usr/bin/env python3
"""
Vocos Vocoder Export Script for Google LiteRT.
Extracts the ConvNeXt backbone and linear spectrogram head, avoiding torch.complex64,
and exports an optimized .tflite FlatBuffer for on-device neural vocoding.
"""

import argparse
import sys
import os
from pathlib import Path

import torch
import numpy as np

# Try importing litert_torch or ai_edge_torch
try:
    import litert_torch
except ImportError:
    try:
        import ai_edge_torch as litert_torch
    except ImportError:
        print("[ERROR] Neither litert_torch nor ai_edge_torch is installed.")
        sys.exit(1)

from vocos import Vocos


class VocosSpecDecoder(torch.nn.Module):
    """
    Decoupled Vocos decoder that computes real and imaginary components of the
    linear spectrogram directly without using torch.complex64 operations,
    enabling native LiteRT MLIR lowering and XNNPACK acceleration.
    """
    def __init__(self, vocos_model: Vocos):
        super().__init__()
        self.backbone = vocos_model.backbone
        self.head_out = vocos_model.head.out

    def forward(self, mel: torch.Tensor) -> torch.Tensor:
        """
        Args:
            mel: [1, 100, seq_len] float32 tensor
        Returns:
            complex_spec: [1, 2, 513, seq_len] float32 tensor (channel 0: real, channel 1: imag)
        """
        x = self.backbone(mel)
        x = self.head_out(x)
        x = x.transpose(1, 2)  # [B, 1026, seq_len]
        mag, phase = x.chunk(2, dim=1)  # Each [B, 513, seq_len]
        mag = torch.exp(mag)
        mag = torch.clip(mag, max=1e2)
        real = mag * torch.cos(phase)
        imag = mag * torch.sin(phase)
        # Stack into [B, 2, 513, seq_len]
        return torch.stack([real, imag], dim=1)


def export_vocos(output_path: Path, seq_len: int = 512):
    print("=" * 78)
    print("           GOOGLE LITERt EXPORT — VOCOS NEURAL VOCODER (FP32)")
    print("=" * 78)
    print(f"Target Destination: {output_path}")
    print(f"Sequence Length:    {seq_len} frames (~{seq_len * 256 / 24000:.2f} seconds)")

    print("\n[Step 1/4] Loading pretrained Vocos model (charactr/vocos-mel-24khz)...")
    vocoder = Vocos.from_pretrained("charactr/vocos-mel-24khz").eval()

    print("\n[Step 2/4] Wrapping Vocos into decoupled real/imag spec module...")
    wrapped_model = VocosSpecDecoder(vocoder).eval()

    dummy_mel = torch.zeros(1, 100, seq_len, dtype=torch.float32)

    print("\n[Step 3/4] Converting PyTorch model to Google LiteRT FlatBuffer...")
    edge_model = litert_torch.convert(wrapped_model, (dummy_mel,))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    edge_model.export(str(output_path))
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  [PASSED] Serialized FlatBuffer: {output_path} ({file_size_mb:.2f} MB)")

    print("\n[Step 4/4] Verifying LiteRT runtime interpreter execution...")
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

    np.random.seed(42)
    test_in = np.random.randn(*in_details[0]["shape"]).astype(np.float32)
    interp.set_tensor(in_details[0]["index"], test_in)
    interp.invoke()
    out_tensor = interp.get_tensor(out_details[0]["index"])

    print(f"  Input Tensor:  {in_details[0]['name']} -> Shape: {in_details[0]['shape']}")
    print(f"  Output Tensor: {out_details[0]['name']} -> Shape: {out_details[0]['shape']}")
    print(f"  Output Min/Max: [{out_tensor.min():.4f}, {out_tensor.max():.4f}]")
    assert not np.isnan(out_tensor).any(), "Output contains NaN values!"
    print("  [PASSED] LiteRT XNNPACK interpreter executed with finite output.")

    print("\n" + "=" * 78)
    print("  🎉 VOCOS LITERt FP32 EXPORT COMPLETE!")
    print("=" * 78 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Export Vocos to LiteRT FP32 FlatBuffer")
    parser.add_argument(
        "--output",
        type=str,
        default="/mnt/c/voice_cloning/models/indicf5/indicf5_vocos_fp32.tflite",
        help="Path to output .tflite file",
    )
    parser.add_argument(
        "--seq_len",
        type=int,
        default=512,
        help="Fixed sequence length in mel frames (default: 512 ~ 5.46 sec)",
    )
    args = parser.parse_args()
    export_vocos(Path(args.output), seq_len=args.seq_len)


if __name__ == "__main__":
    main()
