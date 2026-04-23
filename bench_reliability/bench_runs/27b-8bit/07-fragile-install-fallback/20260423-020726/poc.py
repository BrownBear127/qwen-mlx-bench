#!/usr/bin/env python3
"""
TTS Fallback POC
================
Attempts to synthesize speech using the best available TTS backend.

Fallback order:
  1. piper-tts  (high-quality neural TTS; may need system deps like espeak-ng)
  2. pyttsx3    (offline, OS-native TTS engine wrapper)
  3. Print-only (graceful degradation when nothing is installable)

Usage:
    python poc.py
"""

import importlib
import os
import subprocess
import sys
import tempfile


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TEXT_TO_SYNTHESIZE = "hello world reliability test"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pip_install(*packages: str) -> bool:
    """Attempt to install packages via pip. Returns True on success."""
    try:
        cmd = [
            sys.executable, "-m", "pip", "install",
            "--quiet", "--disable-pip-version-check",
            *packages,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[pip] install failed: {exc}", file=sys.stderr)
        return False


def _try_import(name: str) -> bool:
    """Return True if the module can be imported."""
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Backend: piper-tts
# ---------------------------------------------------------------------------

def _synthesize_piper(text: str, output_path: str) -> bool:
    """Synthesize using piper-tts.

    piper-tts requires a voice model. We try to download a default one
    (en_US-lessac-medium) if it is not already present.
    """
    import piper  # type: ignore

    # Determine where piper stores models
    model_dir = os.path.join(OUTPUT_DIR, "piper_models")
    os.makedirs(model_dir, exist_ok=True)

    # Try common model names
    model_candidates = [
        os.path.join(model_dir, "en_US-lessac-medium.onnx"),
        os.path.join(model_dir, "en_US-amy-medium.onnx"),
        os.path.join(model_dir, "en_US-lessac-low.onnx"),
    ]

    model_path = None
    for candidate in model_candidates:
        if os.path.exists(candidate):
            model_path = candidate
            break

    # If no model found, try to download one
    if model_path is None:
        print("[piper] No voice model found. Attempting to download en_US-lessac-medium ...")
        model_path = os.path.join(model_dir, "en_US-lessac-medium.onnx")
        config_path = os.path.join(model_dir, "en_US-lessac-medium.onnx.json")

        # Use piper's built-in download helper if available
        try:
            from piper.download import download_voice  # type: ignore
            download_voice("en_US-lessac-medium", model_dir)
            # After download, find the .onnx file
            for f in os.listdir(model_dir):
                if f.endswith(".onnx"):
                    model_path = os.path.join(model_dir, f)
                    break
        except Exception as exc:
            print(f"[piper] download_voice failed: {exc}", file=sys.stderr)
            # Try pip-based download
            try:
                subprocess.run(
                    [sys.executable, "-m", "piper", "download", "en_US-lessac-medium",
                     "--output-dir", model_dir],
                    capture_output=True, text=True, timeout=60,
                )
                for f in os.listdir(model_dir):
                    if f.endswith(".onnx"):
                        model_path = os.path.join(model_dir, f)
                        break
            except Exception as exc2:
                print(f"[piper] pip download also failed: {exc2}", file=sys.stderr)
                return False

        if model_path is None or not os.path.exists(model_path):
            print("[piper] Could not obtain a voice model.", file=sys.stderr)
            return False

    # Synthesize
    try:
        # piper.synthesize writes to a file
        piper.synthesize(
            text,
            output=output_path,
            model=model_path,
        )
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as exc:
        print(f"[piper] synthesis failed: {exc}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Backend: pyttsx3
# ---------------------------------------------------------------------------

def _synthesize_pyttsx3(text: str, output_path: str) -> bool:
    """Synthesize using pyttsx3 and save to a WAV file."""
    import pyttsx3  # type: ignore

    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    try:
        engine.runAndWait()
    except Exception as exc:
        print(f"[pyttsx3] runAndWait failed: {exc}", file=sys.stderr)
        return False

    return os.path.exists(output_path) and os.path.getsize(output_path) > 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    text = TEXT_TO_SYNTHESIZE
    backend_used = "none"
    output_file = None

    # --- Attempt 1: piper-tts ---
    if _try_import("piper"):
        print("[info] piper-tts is already installed.")
    else:
        print("[info] piper-tts not found. Attempting to install ...")
        if not _pip_install("piper-tts"):
            print("[info] piper-tts installation failed. Trying next backend.")
        elif not _try_import("piper"):
            print("[info] piper-tts installed but import failed (missing system deps?). Trying next backend.")

    if _try_import("piper"):
        out_path = os.path.join(OUTPUT_DIR, "output_piper.wav")
        print(f"[piper] Synthesizing to {out_path} ...")
        if _synthesize_piper(text, out_path):
            backend_used = "piper-tts"
            output_file = out_path
            print(f"[piper] Success! Output written to {out_path}")
        else:
            print("[piper] Synthesis failed. Trying next backend.")

    # --- Attempt 2: pyttsx3 ---
    if backend_used == "none":
        if _try_import("pyttsx3"):
            print("[info] pyttsx3 is already installed.")
        else:
            print("[info] pyttsx3 not found. Attempting to install ...")
            if not _pip_install("pyttsx3"):
                print("[info] pyttsx3 installation failed. Trying next backend.")
            elif not _try_import("pyttsx3"):
                print("[info] pyttsx3 installed but import failed. Trying next backend.")

        if _try_import("pyttsx3"):
            out_path = os.path.join(OUTPUT_DIR, "output_pyttsx3.wav")
            print(f"[pyttsx3] Synthesizing to {out_path} ...")
            if _synthesize_pyttsx3(text, out_path):
                backend_used = "pyttsx3"
                output_file = out_path
                print(f"[pyttsx3] Success! Output written to {out_path}")
            else:
                print("[pyttsx3] Synthesis failed. Trying next backend.")

    # --- Fallback: print-only ---
    if backend_used == "none":
        backend_used = "print-only (no TTS backend available)"
        print(f"[fallback] would synthesize: {text}")

    # --- Summary ---
    print("\n" + "=" * 50)
    print("TTS POC Summary")
    print("=" * 50)
    print(f"  Backend used : {backend_used}")
    if output_file:
        size_kb = os.path.getsize(output_file) / 1024
        print(f"  Output file  : {output_file} ({size_kb:.1f} KB)")
    else:
        print(f"  Output file  : (none — print-only fallback)")
    print(f"  Input text   : {text}")
    print("=" * 50)


if __name__ == "__main__":
    main()
