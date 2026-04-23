#!/usr/bin/env python3
"""
Minimal POC: Batch-convert a directory of Markdown files to a single EPUB ebook.

Uses Pandoc under the hood. Checks that pandoc is installed before proceeding.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_pandoc():
    """Check if pandoc is installed; print install instructions if not."""
    pandoc_path = shutil.which("pandoc")
    if pandoc_path is None:
        print("ERROR: pandoc is not installed.")
        print("Install it with one of:")
        print("  macOS:   brew install pandoc")
        print("  Ubuntu:  sudo apt install pandoc")
        print("  Windows: choco install pandoc")
        print("  Or download from: https://pandoc.org/installing.html")
        sys.exit(1)
    return pandoc_path


def convert_md_to_epub(md_dir: str, output_epub: str, title: str = "Sample Book"):
    """Convert all .md files in md_dir to a single EPUB using pandoc."""
    md_files = sorted(Path(md_dir).glob("*.md"))
    if not md_files:
        print(f"No .md files found in '{md_dir}'.")
        sys.exit(1)

    print(f"Found {len(md_files)} Markdown file(s) to convert:")
    for f in md_files:
        print(f"  - {f.name}")

    # Build pandoc command
    cmd = [
        "pandoc",
        "-o", output_epub,
        "--metadata", f"title={title}",
        "--metadata", "author=Sample Author",
        "--epub-cover-image", None,  # placeholder
    ]

    # Add all markdown files in sorted order
    for md_file in md_files:
        cmd.append(str(md_file))

    # Remove the None placeholder
    cmd = [c for c in cmd if c is not None]

    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"pandoc failed (exit {result.returncode}):")
        print(result.stderr)
        sys.exit(1)

    return output_epub


def main():
    # Resolve paths relative to this script's directory
    script_dir = Path(__file__).resolve().parent
    md_dir = script_dir / "chapters"
    output_epub = script_dir / "book.epub"

    # Check pandoc
    pandoc_path = check_pandoc()
    print(f"Using pandoc: {pandoc_path}\n")

    # Convert
    epub_path = convert_md_to_epub(str(md_dir), str(output_epub), title="Sample Book")

    # Verify output
    if not output_epub.exists():
        print("ERROR: book.epub was not created.")
        sys.exit(1)

    file_size = output_epub.stat().st_size
    print(f"\n✓ Conversion successful!")
    print(f"  Output file: {epub_path}")
    print(f"  File size:   {file_size:,} bytes ({file_size / 1024:.1f} KB)")

    if file_size <= 1024:
        print("  WARNING: Output file is suspiciously small (< 1 KB).")


if __name__ == "__main__":
    main()
