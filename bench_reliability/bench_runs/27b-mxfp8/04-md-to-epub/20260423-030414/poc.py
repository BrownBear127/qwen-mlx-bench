#!/usr/bin/env python3
"""
POC: Batch-convert a directory of Markdown files into a single EPUB ebook.

Uses pandoc (CLI) to concatenate all .md files in chapters/ and produce book.epub.

Usage:
  uv run --no-project python poc.py
  (no extra Python packages needed — pandoc is a standalone CLI tool)

If pandoc is not installed:
  - macOS:   brew install pandoc
  - Ubuntu:  sudo apt install pandoc
  - Windows: choco install pandoc
  - Or:      https://pandoc.org/installing.html
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Check that pandoc is installed
# ---------------------------------------------------------------------------
pandoc = shutil.which("pandoc")
if pandoc is None:
    print("ERROR: pandoc is not installed or not on PATH.")
    print()
    print("Install instructions:")
    print("  macOS:   brew install pandoc")
    print("  Ubuntu:  sudo apt install pandoc")
    print("  Windows: choco install pandoc")
    print("  General: https://pandoc.org/installing.html")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Gather chapter files
# ---------------------------------------------------------------------------
CHAPTERS_DIR = Path("chapters")
OUTPUT_FILE = Path("book.epub")

if not CHAPTERS_DIR.is_dir():
    print(f"ERROR: Chapters directory '{CHAPTERS_DIR}' not found.")
    sys.exit(1)

md_files = sorted(CHAPTERS_DIR.glob("*.md"))
if not md_files:
    print(f"ERROR: No .md files found in '{CHAPTERS_DIR}'.")
    sys.exit(1)

print(f"Found {len(md_files)} chapter(s) in '{CHAPTERS_DIR}':")
for f in md_files:
    print(f"  - {f.name}")

# ---------------------------------------------------------------------------
# 3. Run pandoc to produce the EPUB
# ---------------------------------------------------------------------------
# --metadata title=...  sets the book title
# --metadata author=... sets the author
# The input files are passed in sorted order so chapters appear correctly.
cmd = [
    pandoc,
    "--output", str(OUTPUT_FILE),
    "--metadata", "title=POC Markdown Book",
    "--metadata", "author=POC Author",
] + [str(f) for f in md_files]

print(f"\nRunning: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode != 0:
    print(f"\nERROR: pandoc failed (exit code {result.returncode})")
    if result.stderr:
        print("stderr:", result.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# 4. Report
# ---------------------------------------------------------------------------
size = OUTPUT_FILE.stat().st_size
print()
print(f"Output file: {OUTPUT_FILE}")
print(f"File size:   {size:,} bytes ({size / 1024:.1f} KB)")
print("Done.")
