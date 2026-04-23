# Markdown to EPUB Converter — Minimal POC

A minimal proof-of-concept that batch-converts a directory of Markdown files into a single EPUB ebook using [Pandoc](https://pandoc.org/).

## Quick Start

```bash
# Ensure pandoc is installed
# macOS:   brew install pandoc
# Ubuntu:  sudo apt install pandoc
# Windows: choco install pandoc

# Run the POC
uv run --no-project --with pandoc python poc.py
```

## What It Does

1. Reads all `.md` files from the `chapters/` directory (sorted alphabetically).
2. Passes them to `pandoc` which merges them into a single EPUB.
3. Prints the output file path and size.

## Files

| File | Description |
|------|-------------|
| `poc.py` | Main script |
| `chapters/chapter1.md` | Sample chapter 1 |
| `chapters/chapter2.md` | Sample chapter 2 |
| `chapters/chapter3.md` | Sample chapter 3 |
| `book.epub` | Generated output (created by running `poc.py`) |

## Requirements

- **Pandoc** (≥ 2.0) — the only dependency. No Python packages needed.

## Notes

- The script checks for `pandoc` on the `PATH` and prints install instructions if missing.
- Markdown files are processed in sorted order so you can control chapter ordering via filenames.
