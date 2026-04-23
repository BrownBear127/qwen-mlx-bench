# Markdown-to-EPUB Batch Converter POC

A minimal proof-of-concept that batch-converts a directory of Markdown files
into a single EPUB ebook.

## How It Works

1. **Scans** the `chapters/` directory for all `.md` files (sorted by filename).
2. **Converts** them into a single `book.epub` using [pandoc](https://pandoc.org)
   via the [pypandoc](https://github.com/jgm/pypandoc) Python wrapper.
3. **Prints** the output file path and size for verification.

## Prerequisites

- **pandoc** must be installed on your system. Install instructions:
  - **macOS**: `brew install pandoc`
  - **Ubuntu/Debian**: `sudo apt install pandoc`
  - **Windows**: `choco install pandoc` (or download from [pandoc.org](https://pandoc.org))
  - **Generic**: See [pandoc.org/installing.html](https://pandoc.org/installing.html)

- **pypandoc** (Python package) — installed automatically via `uv`.

## Usage

```bash
uv run --no-project --with pypandoc python poc.py
```

This will:
- Read `chapters/chapter1.md`, `chapters/chapter2.md`, `chapters/chapter3.md`
- Produce `book.epub` in the current directory
- Print the output path and file size

## Requirements

See `requirements.txt` for pip-installable dependencies.

## Project Structure

```
.
├── poc.py            # Main POC script
├── requirements.txt  # Python dependencies
├── README.md         # This file
├── chapters/
│   ├── chapter1.md
│   ├── chapter2.md
│   └── chapter3.md
└── book.epub         # Generated output (after running poc.py)
```
