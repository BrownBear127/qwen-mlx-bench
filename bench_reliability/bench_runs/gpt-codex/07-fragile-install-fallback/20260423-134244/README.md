# TTS fallback POC

`poc.py` tries three levels in order:

1. `piper-tts`
2. `pyttsx3`
3. plain stdout fallback: `would synthesize: hello world reliability test`

## How it behaves

- `python poc.py` is enough to run it.
- The script does not assume packages are already installed.
- Optional Python packages are installed at runtime into a local `.poc_packages` folder.
- `piper-tts` is treated as usable only if import, voice download, model load, and file generation all succeed.
- If `piper-tts` is unavailable or fails because of system dependencies, model download, wheel issues, or runtime errors, the script falls back to `pyttsx3`.
- On macOS, `pyttsx3` also installs the minimum PyObjC pieces it needs.
- If both backends fail, the script prints the would-do message instead of crashing.

## Output

The script always prints:

- which backend was actually used
- where the output file is, if one was created

If no backend works, it prints:

```text
backend: dry-run
output: none
would synthesize: hello world reliability test
```

## Files it creates

- `output/hello_world_reliability_test.piper.wav` when `piper-tts` succeeds
- `output/hello_world_reliability_test.pyttsx3.aiff` on macOS when `pyttsx3` succeeds
- `output/hello_world_reliability_test.pyttsx3.wav` on non-macOS platforms when `pyttsx3` succeeds

## Optional preinstall

If a verifier wants to install dependencies ahead of time, use `requirements.txt`.
