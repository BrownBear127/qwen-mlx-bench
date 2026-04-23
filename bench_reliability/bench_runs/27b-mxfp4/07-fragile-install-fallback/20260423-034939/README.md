# TTS Synthesis POC — Graceful Fallback

## Overview

This proof-of-concept demonstrates a **graceful fallback strategy** for text-to-speech (TTS) synthesis. It attempts to use increasingly accessible TTS backends, degrading gracefully if none are available — **without ever crashing**.

## Fallback Strategy

The script follows a three-tier fallback chain:

```
piper-tts  ──(fail)──▶  pyttsx3  ──(fail)──▶  "would synthesize: <text>"
   (Tier 1)                (Tier 2)                  (Tier 3)
```

### Tier 1: `piper-tts`

- **What it is**: A fast, high-quality local TTS engine using neural network models.
- **Pros**: Excellent audio quality, fully offline, fast inference.
- **Cons**: Requires system dependencies (e.g., `eSpeak`/`espeak-ng` on macOS), may fail to build wheels on Apple Silicon, needs a voice model (`.onnx` file) which must be downloaded or pre-installed.
- **How the POC handles it**: 
  - Checks if `piper` is importable.
  - If not, attempts `pip install piper-tts` via subprocess.
  - If installed, searches for a voice model in common locations, then tries to download one.
  - Synthesizes audio and writes a WAV file.
  - If any step fails, falls through to Tier 2.

### Tier 2: `pyttsx3`

- **What it is**: A cross-platform offline TTS library that wraps OS-level speech engines.
- **Pros**: Works on Windows (SAPI5), macOS (NSSpeechSynthesizer), and Linux (espeak). No extra model downloads needed.
- **Cons**: Lower audio quality than neural TTS, depends on OS speech engines being present.
- **How the POC handles it**:
  - Checks if `pyttsx3` is importable.
  - If not, attempts `pip install pyttsx3` via subprocess.
  - Uses `engine.save_to_file()` to write a WAV file.
  - If any step fails, falls through to Tier 3.

### Tier 3: Print-only fallback

- If **neither** backend is available or functional, the script prints:
  ```
  would synthesize: hello world reliability test
  ```
- **The script never crashes** — it always produces output.

## Usage

```bash
python poc.py
```

### Prerequisites

If you want the backends to be available, install dependencies:

```bash
pip install -r requirements.txt
```

For `piper-tts` on macOS, you may also need:
```bash
brew install espeak-ng
```

For `pyttsx3` on Linux, you may need:
```bash
sudo apt-get install espeak
```

### Output

The script prints:
1. Which tier it attempted and the result of each attempt.
2. Which backend was **actually used** (or "none" if Tier 3).
3. The path to the output WAV file (or "(none)" if no file was produced).
4. If no backend worked, the `would synthesize: <text>` message.

## File Structure

```
├── poc.py            # Main POC script (run with: python poc.py)
├── requirements.txt  # Python package dependencies (piper-tts, pyttsx3)
└── README.md        # This file
```

## Design Decisions

| Decision | Rationale |
|---|---|
| **Subprocess pip install** | The script must be runnable with just `python poc.py` — no pre-installation. It attempts to install missing packages on the fly. |
| **Graceful degradation** | Every step is wrapped in try/except. The script never raises an unhandled exception. |
| **WAV output** | Both backends can produce WAV files, providing a consistent output format. |
| **No crash guarantee** | Even if pip is unavailable, network is down, or all imports fail, the script completes with a clear message. |
