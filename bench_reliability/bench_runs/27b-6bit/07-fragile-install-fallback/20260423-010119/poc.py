#!/usr/bin/env python3
"""
TTS Fallback POC
================
Attempts to synthesize speech using available TTS backends, with graceful
fallback if none are installable.

Fallback order:
  1. piper-tts  (fast local neural TTS, may need system deps like eSpeak-ng)
  2. pyttsx3    (cross-platform wrapper around OS speech engines)
  3. Print-only (no backend available)

Usage:
    python poc.py
"""

import subprocess
import sys
import os
import importlib


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TEXT_TO_SYNTHESIZE = "hello world reliability test"
OUTPUT_FILENAME = "output.wav"

BACKENDS = [
    {
        "name": "piper-tts",
        "package": "piper-tts",
        "import_name": "piper",
    },
    {
        "name": "pyttsx3",
        "package": "pyttsx3",
        "import_name": "pyttsx3",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def try_import(module_name: str) -> bool:
    """Return True if the module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def install_package(package: str) -> bool:
    """
    Attempt to pip-install a package. Return True on success.

    Tries multiple strategies to handle different environments:
      - Standard pip install
      - With --break-system-packages (PEP 668 environments)
      - With --user flag
    """
    strategies = [
        [sys.executable, "-m", "pip", "install", "--quiet", package],
        [sys.executable, "-m", "pip", "install", "--quiet", "--break-system-packages", package],
        [sys.executable, "-m", "pip", "install", "--quiet", "--user", package],
        [sys.executable, "-m", "pip", "install", "--quiet", "--break-system-packages", "--user", package],
    ]

    for cmd in strategies:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                return True
        except Exception:
            continue

    return False


def try_backend_piper(text: str, output_path: str) -> bool:
    """
    Try to synthesize using piper-tts.

    piper-tts requires a voice model. We attempt to use the default
    en_US-lessac-medium model. If the model is not present we try to
    download it via the piper download command.
    """
    import piper  # noqa: F401  # already verified importable

    # We need to find or download a voice model.
    model_path = None

    # Try common default model locations
    candidates = [
        "en_US-lessac-medium.onnx",
        "en_US-amy-medium.onnx",
        "en_US-lessac-low.onnx",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            model_path = candidate
            break

    # If no model found, try downloading one
    if model_path is None:
        print("  [piper-tts] No voice model found, attempting download...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "piper", "download", "en_US-lessac-medium"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                # The model should now be in the current directory or a
                # known location. Try to find it.
                for candidate in candidates:
                    if os.path.exists(candidate):
                        model_path = candidate
                        break
                # Also check for any .onnx files
                if model_path is None:
                    import glob
                    found = glob.glob("*.onnx")
                    if found:
                        model_path = found[0]
        except Exception:
            pass

    if model_path is None:
        print("  [piper-tts] Could not find or download a voice model.")
        return False

    # Synthesize using the piper CLI (most reliable way)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "piper", "-m", model_path, "-o", output_path],
            input=text,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0 and os.path.exists(output_path):
            return True
    except Exception:
        pass

    # Fallback: try the Python API directly
    try:
        from piper import PiperVoice
        voice = PiperVoice.load(model_path)
        with open(output_path, "wb") as f:
            for chunk in voice.synthesize_stream_raw(text):
                f.write(chunk)
        if os.path.exists(output_path):
            return True
    except Exception:
        pass

    return False


def try_backend_pyttsx3(text: str, output_path: str) -> bool:
    """
    Try to synthesize using pyttsx3.

    pyttsx3 can save to a file using the save_to_file method.
    """
    import pyttsx3  # noqa: F401  # already verified importable

    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        if os.path.exists(output_path):
            return True
    except Exception:
        pass

    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  TTS Fallback POC")
    print("=" * 60)
    print(f"  Text : {TEXT_TO_SYNTHESIZE}")
    print(f"  Output: {OUTPUT_FILENAME}")
    print("=" * 60)
    print()

    used_backend = None
    output_file = None

    for backend in BACKENDS:
        name = backend["name"]
        package = backend["package"]
        import_name = backend["import_name"]

        print(f"[1/3] Trying backend: {name}")

        # Check if already importable
        if not try_import(import_name):
            print(f"  Not installed. Attempting to install {package}...")
            if not install_package(package):
                print(f"  Failed to install {package}. Skipping.")
                print()
                continue
            # Try importing again after install
            if not try_import(import_name):
                print(f"  Installed but cannot import {import_name}. Skipping.")
                print()
                continue

        print(f"  {import_name} is importable. Attempting synthesis...")

        success = False
        if name == "piper-tts":
            success = try_backend_piper(TEXT_TO_SYNTHESIZE, OUTPUT_FILENAME)
        elif name == "pyttsx3":
            success = try_backend_pyttsx3(TEXT_TO_SYNTHESIZE, OUTPUT_FILENAME)

        if success:
            used_backend = name
            output_file = OUTPUT_FILENAME
            print(f"  SUCCESS with {name}!")
            print()
            break
        else:
            print(f"  Synthesis failed with {name}. Trying next backend...")
            # Clean up partial output
            if os.path.exists(OUTPUT_FILENAME):
                os.remove(OUTPUT_FILENAME)
            print()

    # -----------------------------------------------------------------------
    # Report results
    # -----------------------------------------------------------------------
    print("-" * 60)
    print("  RESULT")
    print("-" * 60)

    if used_backend:
        print(f"  Backend used : {used_backend}")
        print(f"  Output file  : {output_file}")
        file_size = os.path.getsize(output_file)
        print(f"  File size    : {file_size} bytes")
    else:
        # Final fallback: print-only mode
        print(f"  Backend used : none (print-only fallback)")
        print(f"  Output file  : (none)")
        print(f"  would synthesize: {TEXT_TO_SYNTHESIZE}")

    print("-" * 60)
    print()
    print("Done.")


if __name__ == "__main__":
    main()
