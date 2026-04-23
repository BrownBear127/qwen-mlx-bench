#!/usr/bin/env python3
"""
POC: Text-to-Speech backend detection with graceful degradation.

Attempts to use piper-tts, then pyttsx3, then falls back to a
"would synthesize" message. Never crashes regardless of environment.
"""

import subprocess
import sys
import os
import json
import tempfile

OUTPUT_FILENAME = "tts_output.wav"


def try_install(package: str, pip_index: str | None = None) -> bool:
    """Attempt to pip-install a package. Returns True on success."""
    cmd = [sys.executable, "-m", "pip", "install", "-q", package]
    if pip_index:
        cmd.extend(["--index-url", pip_index])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def check_installed(package: str) -> bool:
    """Check if a package is already importable without installing."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def try_piper_tts(text: str, output_path: str) -> dict:
    """
    Try piper-tts backend.
    Returns a result dict with status info.
    """
    result = {
        "backend": "piper-tts",
        "success": False,
        "output_file": None,
        "message": "",
    }

    try:
        import piper
    except ImportError:
        result["message"] = "piper-tts not installed"
        return result

    try:
        # Try the Python API first (piper.synthesize or piper.Piper)
        if hasattr(piper, "synthesize"):
            piper.synthesize(text, output_path)
            result["success"] = True
            result["output_file"] = output_path
            result["message"] = "Synthesized via piper-tts (Python API)"
            return result

        if hasattr(piper, "Piper"):
            # Piper class may need a model; try with default
            try:
                piper.Piper().synthesize(text, output_path)
                result["success"] = True
                result["output_file"] = output_path
                result["message"] = "Synthesized via piper-tts (Piper class)"
                return result
            except Exception:
                pass  # Fall through to CLI

        # Fallback: use CLI via subprocess
        # piper CLI requires -m MODEL; try common model names
        models = ["en_US-lessac-medium", "en_US-libritts-r-medium"]
        for model in models:
            cmd = [
                sys.executable, "-m", "piper",
                "-m", model,
                "-f", output_path,
                text,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if proc.returncode == 0 and os.path.exists(output_path):
                result["success"] = True
                result["output_file"] = output_path
                result["message"] = "Synthesized via piper-tts (CLI)"
                return result

        result["message"] = "piper-tts CLI failed (no suitable model found)"
    except Exception as exc:
        result["message"] = f"piper-tts error: {exc}"

    return result


def try_pyttsx3(text: str, output_path: str) -> dict:
    """
    Try pyttsx3 backend (uses system TTS engine).
    Returns a result dict with status info.
    """
    result = {
        "backend": "pyttsx3",
        "success": False,
        "output_file": None,
        "message": "",
    }

    try:
        import pyttsx3
    except ImportError:
        result["message"] = "pyttsx3 not installed"
        return result

    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        if os.path.exists(output_path):
            result["success"] = True
            result["output_file"] = output_path
            result["message"] = "Synthesized via pyttsx3"
        else:
            result["message"] = "pyttsx3 ran but output file not created"
    except Exception as exc:
        result["message"] = f"pyttsx3 error: {exc}"

    return result


def fallback_synthesize(text: str) -> dict:
    """
    Fallback: no TTS backend available.
    Returns a result dict indicating what would have been done.
    """
    return {
        "backend": "none (fallback)",
        "success": False,
        "output_file": None,
        "message": f"would synthesize: {text}",
    }


def main():
    text = "hello world reliability test"
    output_path = os.path.join(os.getcwd(), OUTPUT_FILENAME)

    print("=" * 60)
    print("TTS Backend Detection POC")
    print("=" * 60)
    print(f"Text to synthesize: {text!r}")
    print(f"Output file target: {output_path}")
    print()

    # --- Attempt 1: piper-tts ---
    print("[1/3] Checking piper-tts...")
    if not check_installed("piper"):
        print("      piper-tts not found. Attempting install...")
        installed = try_install("piper-tts")
        if not installed:
            print("      piper-tts install failed.")
    else:
        print("      piper-tts already installed.")

    piper_result = try_piper_tts(text, output_path)
    print(f"      → {piper_result['message']}")

    if piper_result["success"]:
        print()
        print("=" * 60)
        print("RESULT")
        print("=" * 60)
        print(f"Backend used : {piper_result['backend']}")
        print(f"Output file  : {piper_result['output_file']}")
        print(f"Status       : SUCCESS")
        if piper_result["output_file"] and os.path.exists(piper_result["output_file"]):
            size = os.path.getsize(piper_result["output_file"])
            print(f"File size    : {size} bytes")
        return

    # --- Attempt 2: pyttsx3 ---
    print()
    print("[2/3] Checking pyttsx3...")
    if not check_installed("pyttsx3"):
        print("      pyttsx3 not found. Attempting install...")
        installed = try_install("pyttsx3")
        if not installed:
            print("      pyttsx3 install failed.")
    else:
        print("      pyttsx3 already installed.")

    pyttsx3_result = try_pyttsx3(text, output_path)
    print(f"      → {pyttsx3_result['message']}")

    if pyttsx3_result["success"]:
        print()
        print("=" * 60)
        print("RESULT")
        print("=" * 60)
        print(f"Backend used : {pyttsx3_result['backend']}")
        print(f"Output file  : {pyttsx3_result['output_file']}")
        print(f"Status       : SUCCESS")
        if pyttsx3_result["output_file"] and os.path.exists(pyttsx3_result["output_file"]):
            size = os.path.getsize(pyttsx3_result["output_file"])
            print(f"File size    : {size} bytes")
        return

    # --- Attempt 3: Fallback ---
    print()
    print("[3/3] No TTS backend available. Using fallback.")
    fallback_result = fallback_synthesize(text)
    print(f"      → {fallback_result['message']}")

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Backend used : {fallback_result['backend']}")
    print(f"Output file  : {fallback_result['output_file'] or '(none)'}")
    print(f"Status       : FALLBACK (no backend available)")
    print(f"Message      : {fallback_result['message']}")


if __name__ == "__main__":
    main()
