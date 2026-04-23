# Markdown to EPUB POC

This POC uses `pandoc`, which officially supports creating a single EPUB from multiple Markdown source files. Reference:

- https://pandoc.org/epub.html
- https://pandoc.org/installing.html

## What it does

Running `poc.py` will:

- create `chapters/chapter1.md`, `chapters/chapter2.md`, and `chapters/chapter3.md`
- combine those three files into `book.epub`
- print the absolute output path and file size
- fail if `book.epub` was not created or is `<= 1024` bytes

## Requirements

- Python 3
- `pandoc` available on `PATH`

Install `pandoc` if needed:

- macOS (Homebrew): `brew install pandoc`
- Ubuntu/Debian: `sudo apt-get install pandoc`
- Official guide: https://pandoc.org/installing.html

## Run

No third-party Python packages are required, so `requirements.txt` is intentionally omitted.

```bash
uv run --no-project python poc.py
```

If you want to keep the `uv run --with ...` form, the script still works because it only uses the Python standard library:

```bash
uv run --no-project --with anyio python poc.py
```

## Expected output

```text
Output file: /absolute/path/to/book.epub
Size: 12345 bytes
```
