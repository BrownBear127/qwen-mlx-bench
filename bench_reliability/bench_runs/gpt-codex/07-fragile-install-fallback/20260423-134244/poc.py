from __future__ import annotations

import importlib
import socket
import subprocess
import sys
import time
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional


TEXT = "hello world reliability test"
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
PACKAGES_DIR = BASE_DIR / ".poc_packages"
PIPER_VOICE_DIR = BASE_DIR / ".piper_voice"
PIPER_VOICE_NAME = "en_US-lessac-low"
INSTALL_TIMEOUT_SECONDS = 300
FILE_WAIT_TIMEOUT_SECONDS = 15


@dataclass
class Outcome:
    backend: str
    output_path: Optional[Path]
    would_synthesize: bool
    errors: list[str] = field(default_factory=list)


def pyttsx3_packages_for_platform(platform_name: str) -> list[str]:
    if platform_name == "darwin":
        return ["pyttsx3", "pyobjc-core", "pyobjc-framework-Cocoa"]

    return ["pyttsx3"]


def choose_backend(
    text: str,
    output_dir: Path,
    attempts: Iterable[tuple[str, Callable[[str, Path], Path]]],
) -> Outcome:
    errors: list[str] = []
    for backend_name, attempt in attempts:
        try:
            output_path = attempt(text, output_dir)
            if not output_path.is_absolute():
                output_path = output_path.absolute()
            return Outcome(
                backend=backend_name,
                output_path=output_path,
                would_synthesize=False,
                errors=errors,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{backend_name}: {exc}")

    return Outcome(
        backend="dry-run",
        output_path=None,
        would_synthesize=True,
        errors=errors,
    )


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def add_packages_dir_to_path() -> None:
    ensure_directory(PACKAGES_DIR)
    packages_dir = str(PACKAGES_DIR)
    if packages_dir not in sys.path:
        sys.path.insert(0, packages_dir)


def clear_import_state(module_name: str) -> None:
    for loaded_name in list(sys.modules):
        if loaded_name == module_name or loaded_name.startswith(f"{module_name}."):
            sys.modules.pop(loaded_name, None)


def install_packages(packages: list[str]) -> None:
    ensure_directory(PACKAGES_DIR)
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--target",
        str(PACKAGES_DIR),
        *packages,
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=INSTALL_TIMEOUT_SECONDS,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(format_install_error(packages, completed))


def format_install_error(packages: list[str], completed: subprocess.CompletedProcess[str]) -> str:
    details = completed.stderr.strip() or completed.stdout.strip() or "no output"
    compact_details = " | ".join(line.strip() for line in details.splitlines()[-6:] if line.strip())
    return f"install failed for {', '.join(packages)}: {compact_details}"


def ensure_importable(module_name: str, packages: list[str]):
    add_packages_dir_to_path()
    importlib.invalidate_caches()
    try:
        return importlib.import_module(module_name)
    except Exception:  # noqa: BLE001
        clear_import_state(module_name)

    install_packages(packages)
    importlib.invalidate_caches()
    clear_import_state(module_name)
    return importlib.import_module(module_name)


def wait_for_file(path: Path, timeout_seconds: float = FILE_WAIT_TIMEOUT_SECONDS) -> Path:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if path.exists() and path.stat().st_size > 0:
            return path if path.is_absolute() else path.absolute()
        time.sleep(0.1)

    raise RuntimeError(f"output file was not created at {path}")


def synthesize_with_piper(text: str, output_dir: Path) -> Path:
    ensure_importable("piper", ["piper-tts"])
    from piper import PiperVoice
    from piper.download_voices import download_voice

    ensure_directory(output_dir)
    ensure_directory(PIPER_VOICE_DIR)
    socket.setdefaulttimeout(60)

    download_voice(PIPER_VOICE_NAME, PIPER_VOICE_DIR)
    model_path = PIPER_VOICE_DIR / f"{PIPER_VOICE_NAME}.onnx"
    output_path = output_dir / "hello_world_reliability_test.piper.wav"

    voice = PiperVoice.load(model_path, download_dir=PIPER_VOICE_DIR)
    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    return wait_for_file(output_path)


def synthesize_with_pyttsx3(text: str, output_dir: Path) -> Path:
    ensure_importable("pyttsx3", pyttsx3_packages_for_platform(sys.platform))
    import pyttsx3

    ensure_directory(output_dir)
    extension = ".aiff" if sys.platform == "darwin" else ".wav"
    output_path = output_dir / f"hello_world_reliability_test.pyttsx3{extension}"

    engine = pyttsx3.init()
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()
    return wait_for_file(output_path)


def print_outcome(outcome: Outcome, text: str) -> None:
    print(f"backend: {outcome.backend}")
    if outcome.output_path is None:
        print("output: none")
        print(f"would synthesize: {text}")
        return

    print(f"output: {outcome.output_path}")


def main() -> int:
    output_dir = ensure_directory(OUTPUT_DIR)
    outcome = choose_backend(
        TEXT,
        output_dir,
        [
            ("piper-tts", synthesize_with_piper),
            ("pyttsx3", synthesize_with_pyttsx3),
        ],
    )
    print_outcome(outcome, TEXT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
