# TTS Backend Detection POC

## Overview

This proof-of-concept demonstrates graceful degradation when synthesizing text-to-speech in Python. It attempts multiple TTS backends in order of preference and falls back to a "would synthesize" message if none are available.

## Fallback Strategy

The POC tries backends in this order:

1. **piper-tts** — A fast, high-quality local TTS engine. Requires system dependencies (eSpeak/espeak-ng on macOS, various libs on Linux). May fail to build wheels on Apple Silicon without proper toolchain setup.

2. **pyttsx3** — A cross-platform TTS library that wraps system engines (SAPI5 on Windows, NSSpeechSynthesizer on macOS, espeak on Linux). Lightweight but quality depends on the system engine.

3. **Fallback** — If neither library can be imported (even after attempting `pip install`), the script prints `would synthesize: hello world reliability test` instead of crashing.

## Usage

```bash
# Run directly — the script attempts to install missing packages
python poc.py
```

No pre-installation is required. The script uses `subprocess` to run `pip install` internally if a backend is missing.

## Output

The script prints:
- Which backend was checked and whether it was installed
- Whether installation was attempted and succeeded
- The final result: backend used, output file path (if any), and status

## Requirements

If you want to skip the install-attempt step, create a `requirements.txt`:

```
piper-tts
pyttsx3
```

Then install with:
```bash
pip install -r requirements.txt
python poc.py
```

## System Dependencies

| Backend | macOS | Linux | Windows |
|---------|-------|-------|---------|
| piper-tts | espeak-ng (`brew install espeak-ng`) | libespeak1 / espeak-ng | N/A (wheel) |
| pyttsx3 | Built-in NSSpeechSynthesizer | espeak | Built-in SAPI5 |

## Design Decisions

- **Never crashes**: Every backend call is wrapped in try/except
- **No pre-install**: The script installs packages itself via subprocess
- **Single output file**: All backends target the same `tts_output.wav` path
- **Clear result reporting**: At the end, prints which backend won and where the output is
