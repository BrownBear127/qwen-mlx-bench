# TTS Fallback POC

## Overview

This proof-of-concept demonstrates a **graceful fallback strategy** for text-to-speech
synthesis. It attempts to use the best available TTS backend and degrades gracefully
if none can be installed or used.

## Fallback Strategy

The script tries backends in the following order:

| Priority | Backend     | Type              | Notes                                                                 |
|----------|-------------|-------------------|-----------------------------------------------------------------------|
| 1        | `piper-tts` | Neural TTS        | High-quality offline TTS. Requires a voice model (auto-downloaded).   |
| 2        | `pyttsx3`   | OS-native wrapper | Uses system speech engines (SAPI5 on Windows, NSSpeech on macOS, etc.)|
| 3        | Print-only  | Degradation       | Prints `would synthesize: <text>` if no backend is available.         |

### How it works

1. **Import check** — Before attempting installation, the script checks if the module
   is already importable.

2. **Auto-install** — If the module is not found, `pip install` is invoked via
   `subprocess`. This happens at runtime so the user only needs to run
   `python poc.py`.

3. **Import re-check** — After installation, the script verifies the module can
   actually be imported. This catches cases where pip succeeds but the library
   fails to load (e.g., missing system dependencies like `espeak-ng` for
   `piper-tts` on macOS).

4. **Synthesis attempt** — If the module imports, the script tries to synthesize
   speech. If synthesis fails (e.g., missing voice model, engine error), it falls
   through to the next backend.

5. **Graceful degradation** — If all backends fail, the script prints a
   `would synthesize: <text>` message and exits cleanly (exit code 0).

## Usage

```bash
python poc.py
```

No pre-installation is required. The script handles package installation
automatically.

## Requirements

If you want to pre-install dependencies:

```bash
pip install -r requirements.txt
```

## Output

The script prints:
- Which backend was used
- The path to the output WAV file (if any)
- The input text that was synthesized

Example output with `piper-tts`:
```
[info] piper-tts is already installed.
[piper] Synthesizing to ./output_piper.wav ...
[piper] Success! Output written to ./output_piper.wav

==================================================
TTS POC Summary
==================================================
  Backend used : piper-tts
  Output file  : ./output_piper.wav (12.3 KB)
  Input text   : hello world reliability test
==================================================
```

Example output with no backends available:
```
[info] piper-tts not found. Attempting to install ...
[info] piper-tts installation failed. Trying next backend.
[info] pyttsx3 not found. Attempting to install ...
[info] pyttsx3 installation failed. Trying next backend.
[fallback] would synthesize: hello world reliability test

==================================================
TTS POC Summary
==================================================
  Backend used : print-only (no TTS backend available)
  Output file  : (none — print-only fallback)
  Input text   : hello world reliability test
==================================================
```

## Files

| File            | Description                                    |
|-----------------|------------------------------------------------|
| `poc.py`        | Main script — run with `python poc.py`         |
| `requirements.txt` | Pip dependencies (for pre-installation)    |
| `README.md`     | This file                                      |

## Known Issues

- **piper-tts on macOS**: May require `espeak-ng` (`brew install espeak-ng`).
  The script will fall back to `pyttsx3` if piper fails.
- **piper-tts on Apple Silicon**: Wheel builds may fail. The script handles
  this gracefully by falling back.
- **pyttsx3 on Linux**: Requires a speech dispatcher (e.g., `speech-dispatcher`).
  Falls back to print-only if unavailable.
