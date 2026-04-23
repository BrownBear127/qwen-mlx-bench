from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHAPTERS_DIR = ROOT / "chapters"
OUTPUT_PATH = ROOT / "book.epub"

CHAPTERS = {
    "chapter1.md": """# Chapter 1

The morning train cut across the coast while the town was still deciding whether to wake. Salt hung in the air, and every window along the harbor reflected the same pale stripe of light.

Mira kept a notebook on her lap, not because she had anything urgent to write, but because blank paper made the day feel open. She wrote down small details anyway: the gull circling above the dock, the boy carrying oranges, the woman laughing into her scarf.

By the time the train stopped, the page held enough fragments to suggest a beginning. That was usually all she needed.
""",
    "chapter2.md": """# Chapter 2

At noon the market shifted into its louder rhythm. Vendors called across narrow aisles, bicycles rattled over loose stone, and steam rose from the food stalls in quick white ribbons.

Mira followed the crowd until she reached a bookseller working from stacked wooden crates. Most of the covers were faded, but each one looked as if it had been chosen with unusual care. The bookseller spoke softly, like someone protecting a secret from the wind.

She bought a thin travel journal with half its pages still empty. It felt less like a purchase and more like permission.
""",
    "chapter3.md": """# Chapter 3

Evening brought a softer kind of motion. Lamps came on one by one, boats tapped against the pier, and conversations thinned into the low, steady sound of people settling in.

Back in her room, Mira spread the day across the table: two notebooks, a train ticket, a map with folded corners, and a receipt stained with tea. None of it looked important on its own, but together it suggested shape and sequence.

She began writing before the room had fully gone dark. Outside, the harbor kept moving. Inside, the first clean draft of the book finally started to arrive.
""",
}


def ensure_pandoc() -> str:
    pandoc = shutil.which("pandoc")
    if pandoc:
        return pandoc

    message = "\n".join(
        [
            "pandoc is required to build book.epub but was not found on PATH.",
            "Install instructions:",
            "  macOS (Homebrew): brew install pandoc",
            "  Ubuntu/Debian: sudo apt-get install pandoc",
            "  Official docs: https://pandoc.org/installing.html",
        ]
    )
    print(message, file=sys.stderr)
    raise SystemExit(1)


def write_sample_chapters() -> list[Path]:
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    chapter_paths: list[Path] = []
    for name, content in CHAPTERS.items():
        path = CHAPTERS_DIR / name
        path.write_text(content, encoding="utf-8")
        chapter_paths.append(path)

    return sorted(chapter_paths)


def build_epub(pandoc: str, chapter_paths: list[Path]) -> None:
    command = [
        pandoc,
        "--from=markdown",
        "--to=epub3",
        "--toc",
        "--metadata=title=Sample Markdown Book",
        "--metadata=creator=POC Generator",
        "--metadata=language=en-US",
        "-o",
        str(OUTPUT_PATH),
        *[str(path) for path in chapter_paths],
    ]

    subprocess.run(command, check=True, cwd=ROOT)


def main() -> None:
    pandoc = ensure_pandoc()
    chapter_paths = write_sample_chapters()
    build_epub(pandoc, chapter_paths)

    if not OUTPUT_PATH.exists():
        raise RuntimeError("book.epub was not created.")

    size = OUTPUT_PATH.stat().st_size
    if size <= 1024:
        raise RuntimeError(f"book.epub is too small: {size} bytes")

    print(f"Output file: {OUTPUT_PATH}")
    print(f"Size: {size} bytes")


if __name__ == "__main__":
    main()
