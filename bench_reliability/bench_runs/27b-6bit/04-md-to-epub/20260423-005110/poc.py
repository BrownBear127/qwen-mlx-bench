#!/usr/bin/env python3
"""
POC: Batch-convert a directory of Markdown files into a single EPUB ebook.

Uses Pandoc (https://pandoc.org/) as the conversion engine.
Pandoc is a universal document converter that handles Markdown → EPUB
with proper table of contents, metadata, and formatting.

Usage:
    uv run --no-project --with -- python poc.py
    # (no extra pip packages needed — pandoc is a CLI tool)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

CHAPTERS_DIR = Path("chapters")
OUTPUT_EPUB = Path("book.epub")
PANDOC_BIN = "pandoc"


def check_pandoc_installed() -> bool:
    """Return True if pandoc is available on PATH."""
    return shutil.which(PANDOC_BIN) is not None


def print_install_instructions() -> None:
    """Print OS-specific instructions for installing pandoc."""
    plat = sys.platform
    print("\n" + "=" * 60)
    print("  Pandoc is not installed. Please install it first:")
    print("=" * 60)
    if plat == "linux":
        print("\n  Ubuntu/Debian:")
        print("    sudo apt install pandoc")
        print("\n  Fedora:")
        print("    sudo dnf install pandoc")
        print("\n  Arch Linux:")
        print("    sudo pacman -S pandoc")
        print("\n  Or via the installer script:")
        print("    curl -fsSL https://github.com/jgm/pandoc/releases/latest/download/pandoc-3.4-linux-amd64.tar.gz | tar xz")
        print("    sudo mv pandoc-3.4/bin/pandoc /usr/local/bin/")
    elif plat == "darwin":
        print("\n  macOS (Homebrew):")
        print("    brew install pandoc")
        print("\n  macOS (MacPorts):")
        print("    sudo port install pandoc")
    elif plat == "win32":
        print("\n  Windows (Chocolatey):")
        print("    choco install pandoc")
        print("\n  Windows (Scoop):")
        print("    scoop install pandoc")
        print("\n  Or download from: https://pandoc.org/installing.html")
    else:
        print("\n  Visit https://pandoc.org/installing.html for instructions.")
    print("=" * 60 + "\n")


def gather_chapter_files(chapters_dir: Path) -> list[Path]:
    """Collect .md files from the chapters directory, sorted by name."""
    if not chapters_dir.is_dir():
        print(f"Error: chapters directory '{chapters_dir}' not found.")
        sys.exit(1)

    md_files = sorted(chapters_dir.glob("*.md"))
    if not md_files:
        print(f"Error: no .md files found in '{chapters_dir}'.")
        sys.exit(1)

    return md_files


def convert_to_epub(chapter_files: list[Path], output: Path) -> None:
    """Run pandoc to convert all chapter files into a single EPUB."""
    cmd = [
        PANDOC_BIN,
        "--metadata", "title=Sample EPUB Book",
        "--metadata", "author=POC Author",
        "--toc",
        "-o", str(output),
    ] + [str(f) for f in chapter_files]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"\nError: pandoc failed (exit code {result.returncode})")
        if result.stderr:
            print(f"stderr: {result.stderr}")
        sys.exit(1)

    if result.stdout:
        print(f"stdout: {result.stdout}")


def main() -> None:
    # 1. Check pandoc availability
    if not check_pandoc_installed():
        print_install_instructions()
        sys.exit(1)

    # 2. Gather chapter files
    chapter_files = gather_chapter_files(CHAPTERS_DIR)
    print(f"Found {len(chapter_files)} chapter(s):")
    for f in chapter_files:
        print(f"  - {f.name}")

    # 3. Convert
    convert_to_epub(chapter_files, OUTPUT_EPUB)

    # 4. Report results
    if OUTPUT_EPUB.exists():
        size = OUTPUT_EPUB.stat().st_size
        print(f"\n{'=' * 40}")
        print(f"  Output file: {OUTPUT_EPUB.resolve()}")
        print(f"  File size:   {size:,} bytes ({size / 1024:.1f} KB)")
        print(f"{'=' * 40}")
    else:
        print("Error: EPUB file was not created.")
        sys.exit(1)


if __name__ == "__main__":
    main()
