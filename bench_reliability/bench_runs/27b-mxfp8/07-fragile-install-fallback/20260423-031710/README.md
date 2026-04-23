# TTS POC — Graceful Fallback

## Overview

This proof-of-concept demonstrates a **resilient text-to-speech pipeline** that
attempts to synthesise speech using the best available backend, degrading gracefully
if system dependencies or platform constraints prevent installation.

## Fallback Strategy

The script tries backends in this order:

| Priority | Library   | Notes |
|----------|-----------|-------|
| 1        | `piper-tts` | Fast, offline, high-quality neural TTS. Requires a voice model download. May fail on Apple Silicon (no pre-built wheels) or without eSpeak-ng on macOS. |
| 2        | `pyttsx3`   | Cross-platform wrapper around OS-level TTS engines (SAPI5 on Windows, NSSpeechSynthesizer on macOS, eSpeak on Linux). No model download needed. |
| 3        | *Fallback*  | If neither library can be imported or used, prints `would synthesize: <text>` and exits cleanly. |

### Why this order?

- **`piper-tts`** produces the highest quality output and works fully offline.
- **`pyttsx3`** is more likely to install because it has no C-extension build
  requirements and uses the OS's built-in TTS engine.
- The **fallback** ensures the script never crashes, even in a completely bare
  environment.

## How It Works

1. **Import check** — For each backend, the script first tries to `import` the
   library. If it fails, it runs `pip install` and retries.
2. **Synthesis** — If the import succeeds, it attempts to synthesise the text
   `"hello world reliability test"` to `output.wav`.
3. **Graceful degradation** — If synthesis fails (e.g., missing voice model,
   platform incompatibility), the script moves to the next backend.
4. **Summary** — At the end, it prints which backend was used and where the
   output file is (or confirms fallback mode).

## Usage

```bash
# The script handles its own dependencies — no pre-installation needed.
python poc.py
```

If you want to pre-install dependencies (faster on repeated runs):

```bash
pip install -r requirements.txt
python poc.py
```

## Output

Example output when `piper-tts` is available:

```
[backend] Trying piper-tts …
[piper] Success — wrote output.wav

============================================================
  TTS POC — Summary
============================================================
  Text     : hello world reliability test
  Backend  : piper-tts
  Output   : output.wav (123456 bytes)
============================================================
```

Example output when no backend is available:

```
[import] 'piper' not found — attempting to install 'piper-tts' …
[pip] install failed (rc=1): …
[import] 'pyttsx3' not found — attempting to install 'pyttsx3' …
[pip] install failed (rc=1): …
[fallback] No TTS backend available — would synthesize: hello world reliability test

============================================================
  TTS POC — Summary
============================================================
  Text     : hello world reliability test
  Backend  : none (fallback)
  Output   : (none — fallback mode)
============================================================
```

## Known Issues

- **Apple Silicon (M1/M2/M3)**: `piper-tts` may not have pre-built wheels.
  The script will fall back to `pyttsx3` automatically.
- **macOS without eSpeak-ng**: `piper-tts` depends on eSpeak-ng for certain
  voice models. If not installed, synthesis may fail and the script falls back.
- **Docker / minimal environments**: `pyttsx3` may fail if no OS TTS engine
  is present. The fallback message will be printed.

## Files

| File             | Purpose |
|------------------|---------|
| `poc.py`         | Main script — run with `python poc.py` |
| `requirements.txt` | Third-party packages for pre-installation |
| `README.md`      | This file |
