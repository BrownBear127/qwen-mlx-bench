#!/usr/bin/env python
"""
POC: Batch-convert a directory of Markdown files into a single EPUB ebook.

Uses pypandoc (Python wrapper for pandoc) to merge multiple .md files
and convert them into one EPUB.

Usage:
    uv run --no-project --with pypandoc python poc.py
"""

import os
import sys
import glob
import subprocess

CHAPTERS_DIR = "chapters"
OUTPUT_EPUB = "book.epub"


def check_pandoc():
    """Verify pandoc is installed and accessible."""
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError("pandoc returned non-zero exit code")
        first_line = result.stdout.splitlines()[0]
        print(f"Found: {first_line}")
        return True
    except FileNotFoundError:
        print("ERROR: pandoc is not installed.", file=sys.stderr)
        print(
            "Install instructions:\n"
            "  macOS:   brew install pandoc\n"
            "  Ubuntu:  sudo apt install pandoc\n"
            "  Windows: choco install pandoc  (or download from https://pandoc.org)\n"
            "  Generic: https://pandoc.org/installing.html",
            file=sys.stderr,
        )
        return False


def main():
    # 1. Check pandoc availability
    if not check_pandoc():
        sys.exit(1)

    # 2. Gather all .md files from the chapters directory, sorted by name
    md_files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, "*.md")))
    if not md_files:
        print(f"ERROR: No .md files found in '{CHAPTERS_DIR}/'.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(md_files)} chapter(s):")
    for f in md_files:
        print(f"  - {f}")

    # 3. Convert all markdown files into a single EPUB using pypandoc
    import pypandoc

    output = pypandoc.convert_file(
        md_files,
        "epub",
        outputfile=OUTPUT_EPUB,
        extra_args=[
            "--metadata", f"title=A Sample Book",
            "--metadata", f"author=POC Author",
        ],
    )

    # 4. Verify the output
    if not os.path.isfile(OUTPUT_EPUB):
        print(f"ERROR: Expected output file '{OUTPUT_EPUB}' was not created.", file=sys.stderr)
        sys.exit(1)

    size_bytes = os.path.getsize(OUTPUT_EPUB)
    print(f"\nOutput: {os.path.abspath(OUTPUT_EPUB)}")
    print(f"Size:   {size_bytes:,} bytes ({size_bytes / 1024:.1f} KB)")

    if size_bytes <= 1024:
        print("WARNING: EPUB size is <= 1 KB — this may be too small.", file=sys.stderr)
    else:
        print("SUCCESS: EPUB created and is larger than 1 KB.")


if __name__ == "__main__":
    main()
