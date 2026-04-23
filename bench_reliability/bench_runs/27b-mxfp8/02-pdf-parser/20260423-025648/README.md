# PDF Text Extraction POC

## What it does

`poc.py` downloads a small public PDF from a public URL, extracts the
text from its **first page only**, and prints the first **500 characters**
(no more, no less).

## How to run

```bash
uv run --no-project --with pypdf python poc.py
```

Or install dependencies first:

```bash
pip install -r requirements.txt
python poc.py
```

## Why `pypdf` is cross-platform compatible

**`pypdf` is a 100% pure-Python library** — it has:

- **No C extensions** — unlike `PyMuPDF` (which bundles a C library) or
  `pdfminer.six` (which may pull in C-accelerated dependencies), `pypdf`
  contains zero compiled code.
- **No system commands** — it does not invoke `pdftotext`, `qpdf`, or any
  external binary.
- **No platform-specific dependencies** — it works identically on macOS, Linux,
  and Windows because it relies only on the Python standard library.
- **No macOS-only frameworks** — no Quartz, no CoreGraphics, no Homebrew
  packages.

This makes `pypdf` the ideal choice when you need a PDF parser that runs
anywhere Python runs, with no environment-specific setup.

## Source PDF

The demo PDF is hosted at:
<https://www.orimi.com/pdf-test.pdf>

It is a small (~20 KB), single-page, publicly accessible test document.
