# TTS Fallback POC

## Overview

This Proof of Concept demonstrates a **graceful fallback strategy** for text-to-speech
synthesis. It attempts to use the best available TTS backend and degrades
gracefully if none can be installed or used.

## Fallback Strategy

The script tries backends in the following order:

### 1. `piper-tts` (preferred)
- **What it is**: A fast, local, neural-network-based TTS engine.
- **Pros**: High-quality speech, fully offline, no internet needed after setup.
- **Cons**: Requires system dependencies (e.g., `eSpeak-ng` on macOS/Linux).
  May fail to build wheels on Apple Silicon (ARM64). Needs a voice model
  (`.onnx` file) which the script attempts to download automatically.
- **Install**: `pip install piper-tts`

### 2. `pyttsx3` (fallback)
- **What it is**: A cross-platform wrapper around OS-level speech synthesis
  engines (SAPI5 on Windows, NSSpeechSynthesizer on macOS, eSpeak on Linux).
- **Pros**: Pure Python package, usually installs without system dependencies.
  Uses the OS's built-in voice engine.
- **Cons**: Lower quality than neural TTS. Quality varies by OS.
- **Install**: `pip install pyttsx3`

### 3. Print-only (final fallback)
- If neither backend can be installed or used, the script prints:
  ```
  would synthesize: hello world reliability test
  ```
- This ensures the script **never crashes**, even in a completely bare
  environment with no TTS capabilities.

## How It Works

```
┌─────────────────────────────────────────────┐
│              Start POC                       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Try import      │
         │ piper-tts?      │
         └──┬──────────┬───┘
            │ No       │ Yes
            ▼          ▼
     ┌────────────┐  ┌──────────────┐
     │ pip install │  │ Synthesize   │
     │ piper-tts   │  │ with piper   │
     └──┬─────────┘  └──┬───────────┘
        │               │ Success?
        ▼               │ Yes ──→ Done!
     ┌────────────┐     │
     │ Can import? │     ▼
     └──┬──────┬──┘  ┌─────────────────┐
        │ No   │ Yes │ Try import      │
        ▼      ▼     │ pyttsx3?        │
     ┌────────────┐  └──┬──────────┬───┘
     │ Try next    │     │ No       │ Yes
     │ backend     │     ▼          ▼
     └────────────┘ ┌────────────┐  ┌──────────────┐
                    │ pip install│  │ Synthesize   │
                    │ pyttsx3    │  │ with pyttsx3 │
                    └──┬─────────┘  └──┬───────────┘
                       │               │ Success?
                       ▼               │ Yes ──→ Done!
                    ┌────────────┐     │
                    │ Can import? │     ▼
                    └──┬──────┬──┘  ┌─────────────────┐
                       │ No   │ Yes │ Print fallback   │
                       ▼      ▼     │ "would synthesize│
                    ┌────────────┐  │  <text>"         │
                    │ Print       │  └─────────────────┘
                    │ fallback    │
                    └────────────┘
```

## Usage

```bash
python poc.py
```

The script will:
1. Try each backend in order
2. Attempt to install missing packages via `pip`
3. Synthesize "hello world reliability test" to `output.wav`
4. Print which backend was used and where the output is

## Requirements

No pre-installation is required. The script handles its own dependencies.
However, if you want to pre-install:

```
piper-tts
pyttsx3
```

## Output

- **Success**: Creates `output.wav` in the current directory and prints
  the backend name and file size.
- **No backend available**: Prints `would synthesize: hello world reliability test`
  and reports that no backend was used.

## Notes

- The script has a 120-second timeout for package installation and a 60-second
  timeout for synthesis.
- On first run with `piper-tts`, it may attempt to download a voice model
  (~50-100 MB), which requires an internet connection.
- The script is designed to be **non-destructive**: it will not crash, raise
  unhandled exceptions, or leave partial files behind.
