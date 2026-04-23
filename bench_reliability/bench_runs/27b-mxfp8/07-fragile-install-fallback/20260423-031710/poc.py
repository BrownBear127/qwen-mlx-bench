#!/usr/bin/env python3
"""
POC: TTS synthesis with graceful fallback.

Strategy:
  1. Try `piper-tts` (fast, offline, high quality).
       - Needs system deps (eSpeak-ng) on some platforms.
       - May fail to build wheels on Apple Silicon.
  2. Fallback to `pyttsx3` (uses OS-level TTS: sapi5 on Windows,
       nsss on macOS, eSpeak on Linux).
  3. If neither is available, print a "would synthesize" message.

The script attempts to install missing packages via pip before importing.
It never crashes — every failure path is caught and reported.
"""

import os
import platform
import subprocess
import sys
import textwrap


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pip_install(packages: list[str]) -> bool:
    """Try to install packages via pip. Return True on success."""
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + packages
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return True
        print(f"[pip] install failed (rc={result.returncode}): {result.stderr.strip()[:200]}")
        return False
    except subprocess.TimeoutExpired:
        print("[pip] install timed out after 120s")
        return False
    except Exception as e:
        print(f"[pip] install error: {e}")
        return False


def _try_import(name: str, install_name: str | None = None) -> bool:
    """
    Try to import *name*.  If it fails, attempt pip install of
    *install_name* (or *name*) and try again.
    Returns True if the import ultimately succeeded.
    """
    try:
        __import__(name)
        return True
    except ImportError:
        pass

    pkg = install_name if install_name else name
    print(f"[import] '{name}' not found — attempting to install '{pkg}' …")
    if not _pip_install([pkg]):
        return False

    # Second attempt after install
    try:
        __import__(name)
        return True
    except ImportError:
        print(f"[import] '{name}' still not importable after install.")
        return False


# ---------------------------------------------------------------------------
# Backend implementations
# ---------------------------------------------------------------------------

def _synthesize_piper(text: str, output_path: str) -> bool:
    """Use piper-tts to synthesise *text* to *output_path* (wav)."""
    try:
        import piper  # noqa: F401  # side-effect: registers models
    except ImportError:
        return False

    try:
        from piper import PiperVoice
        from piper.download import find_voice_model, download_voice_model
    except ImportError:
        return False

    # Pick a default voice model
    # piper-tts ships with a list of available voices; we grab the first
    # English one.
    try:
        # Try to find a small English model
        voice_file = find_voice_model("en_US-amy-medium")
        if voice_file is None:
            print("[piper] downloading en_US-amy-medium …")
            voice_file = download_voice_model("en_US-amy-medium")
        if voice_file is None:
            print("[piper] could not locate or download voice model")
            return False
    except Exception as e:
        print(f"[piper] voice model lookup failed: {e}")
        return False

    try:
        voice = PiperVoice.load(voice_file)
    except Exception as e:
        print(f"[piper] failed to load voice: {e}")
        return False

    try:
        with open(output_path, "wb") as f:
            # Piper synthesises to bytes
            audio = voice.synthesize(text)
            f.write(audio)
        return True
    except Exception as e:
        print(f"[piper] synthesis failed: {e}")
        return False


def _synthesize_pyttsx3(text: str, output_path: str) -> bool:
    """Use pyttsx3 to synthesise *text* to *output_path* (wav)."""
    try:
        import pyttsx3
    except ImportError:
        return False

    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"[pyttsx3] synthesis failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    text = "hello world reliability test"
    output_path = "output.wav"

    backend = None
    output_file = None

    # --- Attempt 1: piper-tts -------------------------------------------
    if _try_import("piper", "piper-tts"):
        print("[backend] Trying piper-tts …")
        if _synthesize_piper(text, output_path):
            backend = "piper-tts"
            output_file = output_path
            print(f"[piper] Success — wrote {output_file}")
        else:
            print("[piper] Synthesis failed — falling back.")

    # --- Attempt 2: pyttsx3 ----------------------------------------------
    if backend is None:
        if _try_import("pyttsx3"):
            print("[backend] Trying pyttsx3 …")
            if _synthesize_pyttsx3(text, output_path):
                backend = "pyttsx3"
                output_file = output_path
                print(f"[pyttsx3] Success — wrote {output_file}")
            else:
                print("[pyttsx3] Synthesis failed — falling back.")

    # --- Attempt 3: no backend -------------------------------------------
    if backend is None:
        backend = "none (fallback)"
        print(f"[fallback] No TTS backend available — would synthesize: {text}")

    # --- Summary ---------------------------------------------------------
    print()
    print("=" * 60)
    print("  TTS POC — Summary")
    print("=" * 60)
    print(f"  Text     : {text}")
    print(f"  Backend  : {backend}")
    if output_file and os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"  Output   : {output_file} ({size} bytes)")
    elif output_file:
        print(f"  Output   : {output_file} (file not found after synthesis)")
    else:
        print(f"  Output   : (none — fallback mode)")
    print("=" * 60)


if __name__ == "__main__":
    main()
