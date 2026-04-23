# TTS Fallback POC

## Fallback Strategy

The script attempts three backends in order, moving to the next if the current one fails at any stage (install, import, or runtime):

1. **piper-tts** -- A high-quality neural TTS engine. It often fails to install on macOS/Apple Silicon because it depends on native libraries (eSpeak/espeak-ng) and may lack pre-built wheels. Even when installable, it requires a separate voice model (`.onnx` file) to function, so it will gracefully fall through without one.

2. **pyttsx3** -- A cross-platform TTS wrapper that uses the OS speech engine (NSSpeechSynthesizer on macOS, SAPI5 on Windows, espeak on Linux). Lighter dependencies than piper-tts. If it installs and the OS speech engine is available, it writes a `output.wav` file.

3. **print fallback** -- If neither library is usable, the script prints `would synthesize: <text>` and exits cleanly with no crash.

Each backend is wrapped in a try/except so that import errors, build failures, missing native dependencies, and runtime errors are all caught. The script will **never crash**.

## Usage

```bash
python poc.py
```

The script auto-installs missing packages via `pip` at runtime. If you prefer to pre-install:

```bash
pip install -r requirements.txt
python poc.py
```

## Output

The script prints which backend was used and the path to the output audio file (if any).
