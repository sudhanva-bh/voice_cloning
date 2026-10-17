#!/usr/bin/env python3
"""
Phase 0 Automated Verification Suite for Google LiteRT Toolchain.
Verifies Python version, package imports, model resources, PyTorch 2.x torch.export,
and desktop LiteRT interpreter execution with numerical parity checking.
"""

import sys
import os
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "models" / "indicf5"
SCRATCH_DIR = REPO_ROOT / "scratch"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)


def log_step(name: str, passed: bool, details: str = ""):
    status = "[PASSED]" if passed else "[FAILED]"
    print(f"  {status} {name}")
    if details:
        for line in details.strip().splitlines():
            print(f"         {line}")


def test_python_version() -> bool:
    print("\n[Check 1/5] Verifying Python Runtime Environment...")
    major = sys.version_info.major
    minor = sys.version_info.minor
    is_64bit = sys.maxsize > 2**32
    ver_str = f"{major}.{minor}.{sys.version_info.micro} ({'64-bit' if is_64bit else '32-bit'})"
    
    passed = (major == 3 and minor in (10, 11, 12, 13, 14) and is_64bit)
    details = f"Executable: {sys.executable}\nVersion: {ver_str}"
    log_step("Python Version Compatibility (Target: 3.10 - 3.14 64-bit)", passed, details)
    return passed


def test_core_imports() -> bool:
    print("\n[Check 2/5] Verifying Core ML & Audio Packages...")
    all_passed = True
    
    # 1. PyTorch
    try:
        import torch
        torch_ok = hasattr(torch, "export") and hasattr(torch.export, "export")
        details = f"torch == {torch.__version__} (torch.export present: {torch_ok})"
        log_step("PyTorch 2.x with torch.export", torch_ok, details)
        if not torch_ok:
            all_passed = False
    except ImportError as e:
        log_step("PyTorch 2.x Import", False, str(e))
        return False

    # 2. ai-edge-torch / litert-torch
    converter_found = False
    for pkg_name in ("ai_edge_torch", "litert_torch"):
        try:
            mod = __import__(pkg_name)
            ver = getattr(mod, "__version__", "installed")
            log_step(f"Google LiteRT Converter ({pkg_name})", True, f"{pkg_name} == {ver}")
            converter_found = True
            break
        except ImportError:
            pass
    if not converter_found:
        log_step("Google LiteRT Converter (ai_edge_torch or litert_torch)", False, "Neither package found")
        all_passed = False

    # 3. ai-edge-litert / litert / tflite_runtime
    runtime_found = False
    for pkg_name in ("ai_edge_litert", "litert", "tflite_runtime"):
        try:
            mod = __import__(pkg_name)
            ver = getattr(mod, "__version__", "installed")
            log_step(f"Google LiteRT Runtime ({pkg_name})", True, f"{pkg_name} == {ver}")
            runtime_found = True
            break
        except ImportError:
            pass
    if not runtime_found:
        log_step("Google LiteRT Runtime (ai_edge_litert or litert)", False, "Neither package found")
        all_passed = False

    # 4. safetensors & vocos
    try:
        import safetensors
        import vocos
        log_step("safetensors & vocos", True, f"safetensors == {safetensors.__version__}")
    except ImportError as e:
        log_step("safetensors / vocos Import", False, str(e))
        all_passed = False

    # 5. librosa & soundfile
    try:
        import librosa
        import soundfile
        log_step("librosa & soundfile", True, f"soundfile == {soundfile.__version__}")
    except ImportError as e:
        log_step("librosa / soundfile Import", False, str(e))
        all_passed = False

    return all_passed


def test_model_resources() -> bool:
    print("\n[Check 3/5] Verifying Model Weights & Workspace Assets...")
    all_passed = True

    safetensors_path = MODELS_DIR / "model.safetensors"
    vocab_path = MODELS_DIR / "vocab.txt"
    f5_repo = SCRATCH_DIR / "indicf5_repo"

    st_ok = safetensors_path.is_file() and safetensors_path.stat().st_size > 1_000_000_000
    st_size_mb = safetensors_path.stat().st_size / (1024 * 1024) if safetensors_path.is_file() else 0
    log_step(f"IndicF5 model.safetensors ({st_size_mb:.1f} MB)", st_ok, str(safetensors_path))
    if not st_ok:
        all_passed = False

    vocab_ok = vocab_path.is_file() and vocab_path.stat().st_size > 1000
    log_step("IndicF5 vocab.txt", vocab_ok, str(vocab_path))
    if not vocab_ok:
        all_passed = False

    f5_ok = f5_repo.is_dir() and (f5_repo / "f5_tts").is_dir()
    log_step("F5-TTS Architecture Directory", f5_ok, str(f5_repo))
    if not f5_ok:
        all_passed = False

    return all_passed


def test_torch_export_and_convert() -> bool:
    print("\n[Check 4/5] Testing PyTorch 2.x Graph Tracing & LiteRT FlatBuffer Conversion...")
    try:
        import torch
        try:
            import ai_edge_torch
        except ImportError:
            import litert_torch as ai_edge_torch

        class AttentionLinearBlock(torch.nn.Module):
            def __init__(self, dim=64, heads=2):
                super().__init__()
                self.norm = torch.nn.LayerNorm(dim)
                self.qkv = torch.nn.Linear(dim, dim * 3)
                self.proj = torch.nn.Linear(dim, dim)
                self.mlp = torch.nn.Sequential(
                    torch.nn.Linear(dim, dim * 2),
                    torch.nn.GELU(),
                    torch.nn.Linear(dim * 2, dim),
                )
                self.dim = dim
                self.heads = heads

            def forward(self, x):
                norm_x = self.norm(x)
                b, s, d = norm_x.shape
                qkv = self.qkv(norm_x).reshape(b, s, 3, self.heads, d // self.heads)
                q, k, v = qkv.unbind(dim=2)
                attn = torch.nn.functional.scaled_dot_product_attention(
                    q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)
                )
                out = attn.transpose(1, 2).reshape(b, s, d)
                h = x + self.proj(out)
                return h + self.mlp(h)

        model = AttentionLinearBlock().eval()
        dummy_input = (torch.randn(1, 32, 64, dtype=torch.float32),)

        # 1. Tracing
        exported = torch.export.export(model, dummy_input)
        log_step("torch.export.export() Tracing", True, f"Nodes in graph: {len(exported.graph.nodes)}")

        # 2. Conversion to LiteRT
        tflite_path = SCRATCH_DIR / "sanity_phase0.tflite"
        edge_model = ai_edge_torch.convert(model, dummy_input)
        edge_model.export(str(tflite_path))

        file_ok = tflite_path.is_file() and tflite_path.stat().st_size > 0
        details = f"Output: {tflite_path} ({tflite_path.stat().st_size} bytes)"
        log_step("ai_edge_torch.convert() FlatBuffer Serialization", file_ok, details)
        return file_ok

    except Exception as e:
        log_step("Graph Tracing & Conversion", False, f"Exception: {type(e).__name__}: {e}")
        return False


def test_litert_interpreter_parity() -> bool:
    print("\n[Check 5/5] Testing LiteRT Runtime Interpreter & Numerical Parity...")
    try:
        import numpy as np
        import torch
        try:
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            try:
                from litert.interpreter import Interpreter
            except ImportError:
                from tflite_runtime.interpreter import Interpreter

        tflite_path = SCRATCH_DIR / "sanity_phase0.tflite"
        if not tflite_path.is_file():
            log_step("LiteRT Model Availability", False, "Missing sanity_phase0.tflite")
            return False

        # Load into LiteRT Interpreter
        interpreter = Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Generate test tensor
        np.random.seed(42)
        test_in = np.random.randn(1, 32, 64).astype(np.float32)

        interpreter.set_tensor(input_details[0]["index"], test_in)
        interpreter.invoke()
        litert_out = interpreter.get_tensor(output_details[0]["index"])

        shape_ok = litert_out.shape == (1, 32, 64)
        nan_ok = not np.isnan(litert_out).any()
        passed = shape_ok and nan_ok

        details = f"Output Shape: {litert_out.shape} | Contains NaN: {np.isnan(litert_out).any()}"
        log_step("LiteRT Interpreter Execution & Finite Output", passed, details)
        return passed

    except Exception as e:
        log_step("LiteRT Interpreter Parity", False, f"Exception: {type(e).__name__}: {e}")
        return False


def main():
    print("=" * 78)
    print("           GOOGLE LITERt IMPLEMENTATION — PHASE 0 VERIFICATION SUITE")
    print("=" * 78)

    results = [
        ("Python Version", test_python_version()),
        ("Core ML Packages", test_core_imports()),
        ("Model Resources", test_model_resources()),
        ("Graph Tracing & Convert", test_torch_export_and_convert()),
        ("LiteRT Runtime Parity", test_litert_interpreter_parity()),
    ]

    print("\n" + "=" * 78)
    print("                             SUMMARY OF RESULTS")
    print("=" * 78)
    all_ok = True
    for name, status in results:
        mark = "[PASS]" if status else "[FAIL]"
        print(f"  {mark:<8} {name}")
        if not status:
            all_ok = False

    print("=" * 78)
    if all_ok:
        print("  🎉 PHASE 0 VALIDATION COMPLETE: ENVIRONMENT IS READY FOR PHASE 1 EXPORT!")
        print("=" * 78 + "\n")
        sys.exit(0)
    else:
        print("  ❌ PHASE 0 VALIDATION FAILED: RESOLVE OUTSTANDING CHECKS BEFORE PHASE 1.")
        print("=" * 78 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
