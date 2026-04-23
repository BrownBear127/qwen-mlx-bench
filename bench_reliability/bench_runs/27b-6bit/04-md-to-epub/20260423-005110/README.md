# Markdown → EPUB Batch Converter POC

A minimal proof-of-concept that batch-converts a directory of Markdown files into a single EPUB ebook using [Pandoc](https://pandoc.org/).

## How It Works

1. Scans the `chapters/` directory for all `.md` files (sorted alphabetically).
2. Passes them to `pandoc` as input files, producing a single `book.epub`.
3. Prints the output file path and size.

## Prerequisites

**Pandoc** must be installed on your system. It is a CLI tool (not a Python package).

| OS | Install Command |
|---|---|
| Ubuntu/Debian | `sudo apt install pandoc` |
| Fedora | `sudo dnf install pandoc` |
| Arch Linux | `sudo pacman -S pandoc` |
| macOS (Homebrew) | `brew install pandoc` |
| Windows (Chocolatey) | `choco install pandoc` |
| Windows (Scoop) | `scoop install pandoc` |

See [pandoc.org/installing](https://pandoc.org/installing.html) for more options.

## Usage

```bash
uv run --no-project python poc.py
```

No Python packages are required — the script uses only the standard library and shells out to `pandoc`.

## Project Structure

```
.
├── poc.py              # Main conversion script
├── README.md           # This file
├── chapters/
│   ├── chapter1.md     # Sample chapter 1
│   ├── chapter2.md     # Sample chapter 2
│   └── chapter3.md     # Sample chapter 3
└── book.epub           # Generated output (after running poc.py)
```

## Output

After running, `book.epub` will be created in the project root. The script prints:

- The absolute path of the generated EPUB
- The file size in bytes and KB

## Customization

Edit `poc.py` to change:

- `CHAPTERS_DIR` — source directory for `.md` files
- `OUTPUT_EPUB` — output EPUB filename
- Metadata (`title`, `author`) in the `convert_to_epub()` function
