# PDF Text Extraction POC

## Library Choice: `pypdf`

### Why `pypdf` is cross-platform compatible

`pypdf` is a **pure-Python** PDF library with **zero native (C/Rust) extensions** and **no system-level dependencies**. This makes it fully cross-platform:

| Criterion | Detail |
|---|---|
| **No C extensions** | Entirely written in Python — no compiled binaries to install |
| **No system commands** | Does not call `pdftotext`, `qpdf`, or any external CLI tools |
| **No macOS-only deps** | No reliance on macOS frameworks (CoreGraphics, Quartz, etc.) |
| **No Linux-only deps** | No reliance on `poppler`, `tesseract`, or other Linux packages |
| **Wheel availability** | Published on PyPI as a pure-Python wheel, installable via `pip`/`uv` on any platform |

This contrasts with alternatives like:
- **PyMuPDF** — requires compiled C bindings (platform-specific wheels)
- **pdfplumber** — depends on `pdfminer.six` (fine) but heavier; `pypdf` is lighter
- **pdf2image / pdf2docx** — call external system binaries (`poppler`, `antiword`)

## How to run

```bash
uv run --no-project --with pypdf python poc.py
```

## What it does

1. Downloads a small public-domain PDF (Project Gutenberg's *Alice's Adventures in Wonderland*).
2. Parses the first page using `pypdf.PdfReader`.
3. Prints exactly the first **500 characters** of extracted text.

## Files

| File | Purpose |
|---|---|
| `poc.py` | Main script |
| `requirements.txt` | Third-party dependency (`pypdf`) |
| `README.md` | This file |
