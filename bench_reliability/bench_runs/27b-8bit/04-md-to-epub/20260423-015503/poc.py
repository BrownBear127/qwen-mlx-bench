#!/usr/bin/env python3
"""
POC: Batch-convert a directory of Markdown files into a single EPUB ebook.

Uses pandoc (CLI) as the primary converter. Falls back to a pure-Python
approach (ebooklib + markdown) if pandoc is not available.

Usage:
    uv run --no-project --with pandoc-cli python poc.py
    # or, without pandoc installed (pure Python fallback):
    uv run --no-project --with ebooklib,markdown python poc.py
"""

import os
import sys
import subprocess
import glob
import textwrap


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CHAPTERS_DIR = "chapters"
OUTPUT_EPUB = "book.epub"
BOOK_TITLE = "My Markdown Book"
BOOK_AUTHOR = "POC Author"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_md_files(directory: str) -> list[str]:
    """Return sorted list of .md files in *directory*."""
    pattern = os.path.join(directory, "*.md")
    return sorted(glob.glob(pattern))


def check_pandoc() -> bool:
    """Return True if pandoc is installed and callable."""
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ---------------------------------------------------------------------------
# Method 1 — pandoc (preferred)
# ---------------------------------------------------------------------------

def convert_with_pandoc(md_files: list[str], output: str) -> None:
    """Convert *md_files* to a single EPUB using pandoc."""
    cmd = [
        "pandoc",
        *md_files,
        "-o", output,
        "--metadata", f"title={BOOK_TITLE}",
        "--metadata", f"author={BOOK_AUTHOR}",
        "--toc",
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"pandoc stderr:\n{result.stderr}", file=sys.stderr)
        raise RuntimeError(f"pandoc failed (exit {result.returncode})")
    print(f"pandoc succeeded.")


# ---------------------------------------------------------------------------
# Method 2 — pure Python fallback (ebooklib + markdown)
# ---------------------------------------------------------------------------

def convert_with_ebooklib(md_files: list[str], output: str) -> None:
    """Convert *md_files* to a single EPUB using ebooklib + markdown."""
    # Lazy import so we only need these packages when pandoc is absent.
    from ebooklib import epub
    import markdown

    book = epub.EpubBook()

    # Metadata
    book.set_identifier("poc-epub-001")
    book.set_title(BOOK_TITLE)
    book.set_language("en")
    book.add_author(BOOK_AUTHOR)

    chapters: list[epub.EpubHtml] = []
    spine = ["nav"]

    for i, path in enumerate(md_files, start=1):
        with open(path, encoding="utf-8") as f:
            md_text = f.read()

        # Convert markdown -> HTML
        html_body = markdown.markdown(
            md_text,
            extensions=["extra", "toc", "tables"],
        )

        # Extract chapter title from the first heading
        title = f"Chapter {i}"
        for line in md_text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break

        chapter = epub.EpubHtml(
            title=title,
            file_name=f"chapter_{i}.xhtml",
            lang="en",
        )
        chapter.content = (
            f"<html><head><title>{title}</title></head>"
            f"<body>{html_body}</body></html>"
        )
        book.add_item(chapter)
        chapters.append(chapter)
        spine.append(chapter)

    # Table of contents
    book.toc = chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine

    epub.write_epub(output, book, {})
    print("ebooklib conversion succeeded.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Discover markdown files
    md_files = find_md_files(CHAPTERS_DIR)
    if not md_files:
        print(f"Error: no .md files found in '{CHAPTERS_DIR}/'", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(md_files)} markdown file(s):")
    for f in md_files:
        print(f"  - {f}")

    # 2. Choose conversion method
    if check_pandoc():
        print("\nUsing pandoc for conversion.\n")
        convert_with_pandoc(md_files, OUTPUT_EPUB)
    else:
        print(
            "\npandoc not found. Falling back to pure-Python (ebooklib + markdown).\n"
            "To install pandoc instead, see: https://pandoc.org/installing.html\n"
        )
        convert_with_ebooklib(md_files, OUTPUT_EPUB)

    # 3. Report results
    if not os.path.isfile(OUTPUT_EPUB):
        print(f"Error: '{OUTPUT_EPUB}' was not created.", file=sys.stderr)
        sys.exit(1)

    size = os.path.getsize(OUTPUT_EPUB)
    print(f"\n{'=' * 50}")
    print(f"Output file : {os.path.abspath(OUTPUT_EPUB)}")
    print(f"File size   : {size:,} bytes ({size / 1024:.1f} KB)")
    print(f"{'=' * 50}")

    if size <= 1024:
        print("WARNING: EPUB is suspiciously small (<= 1 KB).", file=sys.stderr)
        sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
