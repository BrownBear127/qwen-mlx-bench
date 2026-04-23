#!/usr/bin/env python3
"""
POC: Text-to-Speech Backend Detection & Synthesis

Attempts to use a TTS library in order of preference:
  1. piper-tts  (high-quality, but needs system deps like espeak-ng)
  2. pyttsx3    (offline, no system deps, uses system voices)
  3. Fallback   (prints what would have been done)

The script never crashes — if no backend is available it prints a
"would synthesize" message and exits cleanly.
"""

import subprocess
import sys
import os
import shutil

OUTPUT_FILENAME = "tts_output.wav"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pip_install(package: str) -> bool:
    """Try to pip-install a package. Returns True on success."""
    print(f"  → Attempting to install '{package}' …")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "--quiet"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"  ✓ '{package}' installed successfully.")
            return True
        else:
            print(f"  ✗ '{package}' install failed: {result.stderr[:200]}")
            return False
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"  ✗ '{package}' install error: {exc}")
        return False


def _try_import(module_name: str) -> bool:
    """Import a module by name. Returns True if importable."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def _detect_system_deps() -> dict:
    """Check for common system-level TTS dependencies."""
    checks = {
        "espeak-ng": shutil.which("espeak-ng") is not None,
        "espeak": shutil.which("espeak") is not None,
        "festival": shutil.which("festival") is not None,
        "flite": shutil.which("flite") is not None,
    }
    return checks


# ---------------------------------------------------------------------------
# Backend implementations
# ---------------------------------------------------------------------------

def _synthesize_piper(text: str, output_path: str) -> bool:
    """Try to synthesize using piper-tts."""
    try:
        import piper
    except ImportError:
        return False

    # Piper needs a model file (.onnx). Look in a models directory.
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "piper_models")
    model_file = None

    if os.path.isdir(model_dir):
        for fname in os.listdir(model_dir):
            if fname.endswith(".onnx"):
                model_file = os.path.join(model_dir, fname)
                break

    if model_file is None:
        print("  ℹ No Piper model found (need a .onnx model file).")
        print("     Download one from https://github.com/rhasspy/piper/releases")
        print("     and place it in the piper_models/ directory.")
        return False

    # Try to synthesize using the Piper Python API
    try:
        piper_instance = piper.Piper(model_file, use_cuda=False)
        with open(output_path, "wb") as f:
            for audio_chunk in piper_instance.synthesize(text):
                f.write(audio_chunk)
        return True
    except Exception as exc:
        print(f"  ✗ Piper synthesis failed: {exc}")
        return False


def _synthesize_pyttsx3(text: str, output_path: str) -> bool:
    """Try to synthesize using pyttsx3."""
    try:
        import pyttsx3
    except ImportError:
        return False

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)

        # save_to_file is supported by the sapi5 and espeak backends
        engine.save_to_file(text, output_path)
        engine.runAndWait()

        if os.path.isfile(output_path):
            return True
        else:
            print("  ℹ pyttsx3 ran but did not produce an output file.")
            print("     (This backend may not support file output on your system.)")
            return False
    except Exception as exc:
        print(f"  ✗ pyttsx3 synthesis failed: {exc}")
        return False


def _synthesize_fallback(text: str) -> str:
    """Fallback: just print what would have been done."""
    msg = f"would synthesize: {text}"
    print(f"  ℹ {msg}")
    return msg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    text = "hello world reliability test"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)

    print("=" * 60)
    print("  TTS Backend Detection POC")
    print("=" * 60)
    print(f"  Text to synthesize: \"{text}\"")
    print(f"  Output file:        {output_path}")
    print()

    # Check system deps
    system_deps = _detect_system_deps()
    print("  System dependencies detected:")
    for dep, found in system_deps.items():
        status = "✓" if found else "✗"
        print(f"    {status} {dep}")
    print()

    # ---- Backend 1: piper-tts ----
    print("-" * 40)
    print("  Backend 1: piper-tts")
    print("-" * 40)

    if not _try_import("piper"):
        print("  ℹ piper not installed; attempting install …")
        if not _pip_install("piper-tts"):
            print("  ✗ piper-tts not available (skipping).")
    else:
        print("  ✓ piper already available.")

    if _try_import("piper"):
        if _synthesize_piper(text, output_path):
            print(f"  ✓ Synthesized with piper-tts → {output_path}")
            print()
            print("=" * 60)
            print(f"  RESULT: Backend = piper-tts, Output = {output_path}")
            print("=" * 60)
            return

    # ---- Backend 2: pyttsx3 ----
    print()
    print("-" * 40)
    print("  Backend 2: pyttsx3")
    print("-" * 40)

    if not _try_import("pyttsx3"):
        print("  ℹ pyttsx3 not installed; attempting install …")
        if not _pip_install("pyttsx3"):
            print("  ✗ pyttsx3 not available (skipping).")
    else:
        print("  ✓ pyttsx3 already available.")

    if _try_import("pyttsx3"):
        if _synthesize_pyttsx3(text, output_path):
            print(f"  ✓ Synthesized with pyttsx3 → {output_path}")
            print()
            print("=" * 60)
            print(f"  RESULT: Backend = pyttsx3, Output = {output_path}")
            print("=" * 60)
            return
        else:
            print("  ✗ pyttsx3 available but synthesis failed.")

    # ---- Backend 3: Fallback ----
    print()
    print("-" * 40)
    print("  Backend 3: Fallback (no TTS backend)")
    print("-" * 40)

    _synthesize_fallback(text)
    print()
    print("=" * 60)
    print("  RESULT: No TTS backend available — no output file produced.")
    print("=" * 60)


if __name__ == "__main__":
    main()
