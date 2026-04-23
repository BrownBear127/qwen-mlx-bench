#!/usr/bin/env python3
"""TTS proof-of-concept with cascading fallback strategy."""

import subprocess
import sys
import os

TEXT = "hello world reliability test"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def try_piper():
    """Attempt to use piper-tts to synthesize speech."""
    try:
        import piper
    except ImportError:
        # Try installing piper-tts via pip
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "piper-tts"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=120,
            )
            import piper
        except Exception:
            return None

    try:
        # piper-tts requires a voice model to be downloaded separately.
        # Without a model path this will fail, so we treat that as unavailable.
        from piper.voice import PiperVoice

        # A real deployment would point to a .onnx voice model here.
        # Since we cannot guarantee one exists, this path is best-effort.
        raise RuntimeError("no voice model available")
    except Exception:
        return None


def try_pyttsx3():
    """Attempt to use pyttsx3 to synthesize speech."""
    try:
        import pyttsx3
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyttsx3"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60,
            )
            import pyttsx3
        except Exception:
            return None

    try:
        engine = pyttsx3.init()
        out_path = os.path.join(OUTPUT_DIR, "output.wav")
        engine.save_to_file(TEXT, out_path)
        engine.runAndWait()
        return out_path
    except Exception:
        return None


def fallback_print():
    """Last-resort fallback: just print the would-do message."""
    print(f"would synthesize: {TEXT}")
    return None


def main():
    # --- Backend 1: piper-tts ---
    result = try_piper()
    if result:
        print(f"Backend used: piper-tts")
        print(f"Output file:  {result}")
        return

    # --- Backend 2: pyttsx3 ---
    result = try_pyttsx3()
    if result and os.path.isfile(result):
        print(f"Backend used: pyttsx3")
        print(f"Output file:  {result}")
        return

    # --- Backend 3: print fallback ---
    fallback_print()
    print("Backend used: print-fallback (no TTS library available)")
    print("Output file:  none")


if __name__ == "__main__":
    main()
