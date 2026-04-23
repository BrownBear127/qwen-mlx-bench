# Markdown → EPUB POC

Batch-convert a directory of Markdown files into a single EPUB ebook using
**ebooklib** and **markdown** (pure Python — no external CLI tools required).

## Quick start

```bash
uv run --no-project --with ebooklib --with markdown python poc.py
```

Or install manually:

```bash
pip install -r requirements.txt
python poc.py
```

## What it does

1. Reads every `*.md` file from `chapters/` (sorted alphabetically).
2. Converts each file's Markdown to HTML.
3. Packages all chapters into a single `book.epub` with a table of contents.
4. Prints the output path and file size.

## Project structure

```
.
├── chapters/
│   ├── chapter1.md
│   ├── chapter2.md
│   └── chapter3.md
├── poc.py
├── requirements.txt
└── README.md
```

## Dependencies

| Package   | Purpose                  |
|-----------|--------------------------|
| ebooklib  | EPUB file creation       |
| markdown  | Markdown → HTML conversion |
