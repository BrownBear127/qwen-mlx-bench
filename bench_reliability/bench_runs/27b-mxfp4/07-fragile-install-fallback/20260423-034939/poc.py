#!/usr/bin/env python3
"""
POC: TTS synthesis with graceful fallback.

Strategy:
  1. Try `piper-tts` (fast, high-quality local TTS).
  2. Fallback to `pyttsx3` (cross-platform, uses OS speech engines).
  3. If neither is available, print a "would synthesize" message.

The script attempts to install missing packages via pip (subprocess) before
importing. If installation fails or the import fails, it degrades gracefully
without crashing.

Usage:
    python poc.py
"""

import subprocess
import sys
import os
import importlib
import shutil

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TEXT = "hello world reliability test"
OUTPUT_FILE = "output.wav"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pip_install(packages: list[str]) -> bool:
    """Attempt to install packages via pip. Returns True on success."""
    pkg_str = " ".join(packages)
    print(f"  -> Attempting to install: {pkg_str}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", pkg_str],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"  -> Successfully installed: {pkg_str}")
            return True
        else:
            print(f"  -> pip install failed (rc={result.returncode}):")
            if result.stderr:
                print(f"     stderr: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print("  -> pip install timed out (120s).")
        return False
    except FileNotFoundError:
        print("  -> pip not found in environment.")
        return False


def _try_import(name: str) -> bool:
    """Try to import a module. Returns True on success."""
    try:
        importlib.import_module(name)
        return True
    except (ImportError, ModuleNotFoundError):
        return False


# ---------------------------------------------------------------------------
# Backend: piper-tts
# ---------------------------------------------------------------------------

def _synthesize_piper(text: str, output_path: str) -> bool:
    """
    Use piper-tts to synthesize text to a WAV file.

    piper-tts requires a voice model. We try to list available models
    and use the first one. If no model is available, we attempt to
    download a small default one.
    """
    import piper  # type: ignore

    print("  -> Using piper-tts backend.")

    # Try to find a voice model
    model_path = None

    # Check common locations for pre-installed models
    candidate_dirs = [
        os.path.expanduser("~/.local/share/piper/voices"),
        "/usr/share/piper/voices",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices"),
    ]

    for d in candidate_dirs:
        if os.path.isdir(d):
            for root, _dirs, files in os.walk(d):
                for f in files:
                    if f.endswith(".onnx"):
                        model_path = os.path.join(root, f)
                        break
                if model_path:
                    break
        if model_path:
            break

    if model_path is None:
        print("  -> No voice model found. Attempting to download a default model...")
        try:
            from piper import download  # type: ignore
            # Try to download a small English model
            model_path = download.download_voice("en_US-lessac-medium")
        except Exception as e:
            print(f"  -> Could not download model: {e}")
            return False

    if model_path is None:
        print("  -> Could not locate or download a voice model for piper-tts.")
        return False

    print(f"  -> Using model: {model_path}")

    try:
        # piper's main entry point
        from piper import PiperVoice  # type: ignore
        voice = PiperVoice.load(model_path)
        # Synthesize
        audio_data = voice.synthesize(text)

        # Write raw audio to file (piper outputs 22050 Hz, 16-bit mono)
        # We'll write as a WAV file
        import wave
        with wave.open(output_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            wav_file.writeframes(audio_data)

        print(f"  -> Output written to: {output_path}")
        return True
    except Exception as e:
        print(f"  -> piper-tts synthesis failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Backend: pyttsx3
# ---------------------------------------------------------------------------

def _synthesize_pyttsx3(text: str, output_path: str) -> bool:
    """
    Use pyttsx3 to synthesize text to a WAV file.

    pyttsx3's save_to_file method writes directly to a file.
    """
    import pyttsx3  # type: ignore

    print("  -> Using pyttsx3 backend.")

    try:
        engine = pyttsx3.init()
        # Some platforms support setting the output file format
        engine.save_to_file(text, output_path)
        engine.runAndWait()

        if os.path.exists(output_path):
            print(f"  -> Output written to: {output_path}")
            return True
        else:
            print("  -> pyttsx3 did not produce an output file.")
            return False
    except Exception as e:
        print(f"  -> pyttsx3 synthesis failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("TTS Synthesis POC - Graceful Fallback")
    print("=" * 60)
    print(f"Text to synthesize: {TEXT!r}")
    print()

    backend_used = "none"
    output_path = None

    # ------------------------------------------------------------------
    # Stage 1: Try piper-tts
    # ------------------------------------------------------------------
    print("[1/3] Attempting piper-tts ...")
    if not _try_import("piper"):
        if not _pip_install(["piper-tts"]):
            print("  -> piper-tts installation failed. Moving to fallback.")
        # Re-check after install attempt
    if _try_import("piper"):
        if _synthesize_piper(TEXT, OUTPUT_FILE):
            backend_used = "piper-tts"
            output_path = OUTPUT_FILE
            print()
            print("=" * 60)
            print(f"SUCCESS: Used backend = {backend_used}")
            print(f"Output file: {output_path}")
            print("=" * 60)
            return
        else:
            print("  -> piper-tts import succeeded but synthesis failed. Moving to fallback.")
    else:
        print("  -> piper-tts not available. Moving to fallback.")

    print()

    # ------------------------------------------------------------------
    # Stage 2: Try pyttsx3
    # ------------------------------------------------------------------
    print("[2/3] Attempting pyttsx3 ...")
    if not _try_import("pyttsx3"):
        if not _pip_install(["pyttsx3"]):
            print("  -> pyttsx3 installation failed. Moving to fallback.")
        # Re-check after install attempt
    if _try_import("pyttsx3"):
        if _synthesize_pyttsx3(TEXT, OUTPUT_FILE):
            backend_used = "pyttsx3"
            output_path = OUTPUT_FILE
            print()
            print("=" * 60)
            print(f"SUCCESS: Used backend = {backend_used}")
            print(f"Output file: {output_path}")
            print("=" * 60)
            return
        else:
            print("  -> pyttsx3 import succeeded but synthesis failed. Moving to fallback.")
    else:
        print("  -> pyttsx3 not available. Moving to fallback.")

    print()

    # ------------------------------------------------------------------
    # Stage 3: No backend available - print would-do message
    # ------------------------------------------------------------------
    print("[3/3] No TTS backend available.")
    print()
    print(f"  would synthesize: {TEXT}")
    print()
    print("=" * 60)
    print(f"RESULT: No TTS backend was available.")
    print(f"  Backend used: {backend_used}")
    print(f"  Output file:  {output_path if output_path else '(none)'}")
    print(f"  Message:      would synthesize: {TEXT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
