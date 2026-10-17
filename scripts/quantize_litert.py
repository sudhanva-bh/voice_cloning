#!/usr/bin/env python3
"""
scripts/quantize_litert.py: Post-Training Quantization (PTQ) for IndicF5 & Vocos FlatBuffers.

Converts FP32 Google LiteRT FlatBuffers into INT8 FlatBuffers using ai_edge_quantizer.
Reduces DiT footprint from 1,288 MB to ~349 MB (73% reduction) and Vocos from 51.65 MB to ~13 MB.

Usage:
    wsl /mnt/c/voice_cloning/litert-wsl-env/bin/python3 scripts/quantize_litert.py [--mode dynamic|full_int8]
"""

import os
import sys
import time
import argparse
from pathlib import Path

try:
    import ai_edge_quantizer as q
    from ai_edge_quantizer import recipe
except ImportError:
    print("[ERROR] ai_edge_quantizer is required. Please run inside the litert-wsl-env virtual environment.")
    sys.exit(1)

try:
    import ai_edge_litert.interpreter as tfl
except ImportError:
    print("[ERROR] ai_edge_litert is required for verification.")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Google LiteRT Post-Training Quantization (PTQ) for IndicF5")
    parser.add_argument(
        "--dit_in",
        type=str,
        default="models/indicf5/indicf5_dit_fp32.tflite",
        help="Path to FP32 DiT FlatBuffer"
    )
    parser.add_argument(
        "--vocos_in",
        type=str,
        default="models/indicf5/indicf5_vocos_fp32.tflite",
        help="Path to FP32 Vocos FlatBuffer"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="models/indicf5",
        help="Destination directory for quantized models"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["dynamic", "full_int8"],
        default="dynamic",
        help="Quantization mode: 'dynamic' (per-channel INT8 weights, dynamic FP32 activations) or 'full_int8'"
    )
    parser.add_argument(
        "--skip_dit",
        action="store_true",
        help="Skip DiT quantization"
    )
    parser.add_argument(
        "--skip_vocos",
        action="store_true",
        help="Skip Vocos quantization"
    )
    return parser.parse_args()


def quantize_model(model_path: str, output_dir: str, model_name: str, mode: str = "dynamic"):
    print(f"\n{'='*70}")
    print(f"[*] Processing: {model_path} -> {model_name}.tflite (Mode: {mode})")
    print(f"{'='*70}")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Input model not found: {model_path}")

    orig_size_bytes = os.path.getsize(model_path)
    orig_size_mb = orig_size_bytes / (1024 * 1024)
    print(f"[+] Original Model Size: {orig_size_mb:.2f} MB ({orig_size_bytes:,} bytes)")

    # 1. Initialize Quantizer
    t0 = time.time()
    print("[+] Initializing ai_edge_quantizer.Quantizer...")
    qt = q.Quantizer(model_path)
    init_time = time.time() - t0
    print(f"[+] Initialized in {init_time:.2f}s")

    # 2. Select and Load Recipe
    if mode == "dynamic":
        # Per-channel symmetric INT8 weights, dynamic float32 activations
        quant_recipe = recipe.dynamic_wi8c_afp32()
        print("[+] Loaded recipe: dynamic_wi8c_afp32 (Per-channel INT8 weights)")
    elif mode == "full_int8":
        quant_recipe = recipe.static_wi8_ai8()
        print("[+] Loaded recipe: static_wi8_ai8 (Full Integer PTQ)")
    else:
        raise ValueError(f"Unknown mode: {mode}")

    qt.load_quantization_recipe(quant_recipe)
    print(f"[+] Calibration Required: {qt.need_calibration}")

    # 3. Execute Quantization
    t1 = time.time()
    print("[+] Executing quantization transformation passes...")
    quant_result = qt.quantize()
    quant_time = time.time() - t1
    print(f"[+] Quantization completed in {quant_time:.2f}s")

    # 4. Save Quantized Model
    os.makedirs(output_dir, exist_ok=True)
    quant_result.save(output_dir, model_name, overwrite=True)

    out_file = os.path.join(output_dir, f"{model_name}.tflite")
    if not os.path.exists(out_file):
        raise RuntimeError(f"Expected output file was not created: {out_file}")

    quant_size_bytes = os.path.getsize(out_file)
    quant_size_mb = quant_size_bytes / (1024 * 1024)
    compression_ratio = (1.0 - (quant_size_bytes / orig_size_bytes)) * 100.0

    print(f"[+] Quantized Model Size: {quant_size_mb:.2f} MB ({quant_size_bytes:,} bytes)")
    print(f"[+] Size Reduction: -{compression_ratio:.1f}% ({orig_size_mb / quant_size_mb:.2f}x smaller)")

    # 5. Sanity Verification via LiteRT Interpreter
    print("[+] Verifying quantized FlatBuffer via LiteRT Interpreter...")
    try:
        interp = tfl.Interpreter(model_path=out_file)
        interp.allocate_tensors()
        in_details = interp.get_input_details()
        out_details = interp.get_output_details()
        print(f"[PASSED] Verification successful! Tensor allocation verified.")
        print(f"         Inputs ({len(in_details)}): {[d['name'] + ' ' + str(d['shape'].tolist()) for d in in_details]}")
        print(f"         Outputs ({len(out_details)}): {[d['name'] + ' ' + str(d['shape'].tolist()) for d in out_details]}")
    except Exception as e:
        print(f"[FAILED] LiteRT Interpreter verification failed: {e}")
        raise

    return {
        "model_name": model_name,
        "input_path": model_path,
        "output_path": out_file,
        "orig_size_mb": orig_size_mb,
        "quant_size_mb": quant_size_mb,
        "reduction_pct": compression_ratio,
        "quant_time_sec": quant_time,
    }


def main():
    args = parse_args()
    print("=" * 70)
    print("Google LiteRT IndicF5 INT8 Post-Training Quantization (Phase 3)")
    print("=" * 70)
    print(f"Input DiT:    {args.dit_in}")
    print(f"Input Vocos:  {args.vocos_in}")
    print(f"Output Dir:   {args.output_dir}")
    print(f"Mode:         {args.mode}")

    results = []

    # Process Vocos First (Fastest, ~10s)
    if not args.skip_vocos:
        vocos_res = quantize_model(
            model_path=args.vocos_in,
            output_dir=args.output_dir,
            model_name="indicf5_vocos_int8",
            mode=args.mode
        )
        results.append(vocos_res)

    # Process DiT (335M parameters, ~15-20s)
    if not args.skip_dit:
        dit_res = quantize_model(
            model_path=args.dit_in,
            output_dir=args.output_dir,
            model_name="indicf5_dit_int8",
            mode=args.mode
        )
        results.append(dit_res)

    # Print Summary Table
    print("\n" + "=" * 70)
    print("Phase 3 Post-Training Quantization Summary")
    print("=" * 70)
    print(f"{'Model':<22} | {'Original (MB)':<14} | {'Quantized (MB)':<15} | {'Reduction':<10} | {'Status'}")
    print("-" * 70)
    for r in results:
        print(f"{r['model_name']:<22} | {r['orig_size_mb']:>10.2f} MB | {r['quant_size_mb']:>11.2f} MB | {r['reduction_pct']:>8.1f}% | [PASSED]")
    print("-" * 70)
    total_orig = sum(r['orig_size_mb'] for r in results)
    total_quant = sum(r['quant_size_mb'] for r in results)
    total_red = (1.0 - (total_quant / total_orig)) * 100.0
    print(f"{'TOTAL ENVELOPE':<22} | {total_orig:>10.2f} MB | {total_quant:>11.2f} MB | {total_red:>8.1f}% | [PASSED]")
    print("=" * 70)
    print("\n[SUCCESS] Phase 3 Quantization completed successfully!")


if __name__ == "__main__":
    main()
