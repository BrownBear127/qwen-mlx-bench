# Markdown → EPUB Batch Converter (POC)

A minimal proof-of-concept that batch-converts a directory of Markdown files
into a single EPUB ebook.

## Tool

**Pandoc** — the universal document converter. It reads all `.md` files in
`chapters/` (in sorted order) and produces a single `book.epub`.

## Prerequisites

Pandoc must be installed on your system:

| Platform | Command |
|----------|---------|
| macOS    | `brew install pandoc` |
| Ubuntu   | `sudo apt install pandoc` |
| Windows  | `choco install pandoc` |
| Any      | https://pandoc.org/installing.html |

No Python packages are required.

## Usage

```bash
# Run the POC
uv run --no-project python poc.py
```

## What it does

1. Checks that `pandoc` is installed (prints install instructions if not).
2. Scans `chapters/` for `*.md` files (sorted alphabetically).
3. Calls pandoc to convert all chapters into `book.epub`.
4. Prints the output file path and size.

## File structure

```
.
├── poc.py              # Main script
├── requirements.txt    # (empty — no Python deps)
├── README.md           # This file
├── chapters/
│   ├── chapter1.md
│   ├── chapter2.md
│   └── chapter3.md
└── book.epub           # Generated output
```
