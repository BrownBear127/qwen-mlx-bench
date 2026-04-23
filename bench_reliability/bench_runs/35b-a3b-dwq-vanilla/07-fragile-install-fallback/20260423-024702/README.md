# TTS Backend Detection POC

## Overview

This proof-of-concept demonstrates a **graceful degradation strategy** for
text-to-speech (TTS) synthesis in Python.  It attempts to use a TTS library
in order of preference and falls back to a no-op message if nothing is
available.

## Fallback Strategy

```
┌─────────────────────────────────────────────────────────┐
│  1. piper-tts                                           │
│     High-quality neural TTS. Requires:                  │
│       • piper-tts Python package                        │
│       • A .onnx model file (download from               │
│         https://github.com/rhasspy/piper/releases)      │
│       • System deps: espeak-ng (macOS: brew install     │
│         espeak-ng) or espeak                            │
│     Fails silently → try next backend                   │
├─────────────────────────────────────────────────────────┤
│  2. pyttsx3                                             │
│     Offline, system-voice based TTS. No extra system    │
│     dependencies needed (uses OS built-in voices).      │
│     May not produce a file on all platforms (e.g. macOS │
│     without espeak installed).                          │
│     Fails silently → try next backend                   │
├─────────────────────────────────────────────────────────┤
│  3. Fallback                                            │
│     Prints: "would synthesize: <text>"                  │
│     No output file is produced.                         │
└─────────────────────────────────────────────────────────┘
```

## How It Works

1. **System dependency scan** — checks for `espeak-ng`, `espeak`,
   `festival`, and `flite` on the PATH.
2. **Backend 1: piper-tts** — tries to import `piper`; if not present,
   runs `pip install piper-tts` via subprocess.  If a `.onnx` model file
   is found in `piper_models/`, it synthesizes audio.
3. **Backend 2: pyttsx3** — same import → install pattern.  Uses
   `engine.save_to_file()` to write a WAV file.
4. **Backend 3: Fallback** — prints the would-do message.  The script
   **never crashes**.

## Files

| File          | Purpose                                          |
|---------------|--------------------------------------------------|
| `poc.py`      | Main script — runnable with `python poc.py`      |
| `requirements.txt` | Third-party Python packages (one per line) |
| `README.md`   | This file                                        |

## Usage

```bash
# Run directly — the script installs missing packages itself
python poc.py

# Or install dependencies first for faster runs
pip install -r requirements.txt
python poc.py
```

## Output

The script prints which backend was used and where the output file is
located (if any).  Example output:

```
============================================================
  TTS Backend Detection POC
============================================================
  Text to synthesize: "hello world reliability test"
  Output file:        ./tts_output.wav

  System dependencies detected:
    ✓ espeak-ng
    ✗ espeak
    ✗ festival
    ✗ flite

  Backend 1: piper-tts
  ✓ piper already available.
  ✓ Synthesized with piper-tts → ./tts_output.wav

============================================================
  RESULT: Backend = piper-tts, Output = ./tts_output.wav
============================================================
```

## Notes

- **piper-tts** on macOS may need `brew install espeak-ng` before it can
  build wheels or run.
- **pyttsx3** on macOS uses the built-in `NSSpeechSynthesizer` by default,
  which does **not** support `save_to_file`.  Install `espeak` via Homebrew
  (`brew install espeak`) to enable file output.
- The fallback path ensures the script is always runnable, even in a
  completely bare environment.
