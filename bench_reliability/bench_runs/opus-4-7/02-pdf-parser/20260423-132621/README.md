# PDF Parser POC

## Chosen library: PyMuPDF (`pymupdf`)

### Why PyMuPDF is cross-platform compatible

PyMuPDF is a Python binding for MuPDF, a lightweight PDF/XPS/EPUB renderer. It is fully cross-platform for the following reasons:

1. **Pre-built wheels for all major platforms** — PyPI hosts binary wheels for macOS (x86_64 and arm64), Linux (x86_64 and aarch64), and Windows. No compilation or system-level package installation is required.
2. **No external system dependencies** — MuPDF is statically linked into the wheel. Unlike tools such as `pdftotext` (which requires Poppler) or `textract` (which shells out to OS commands), PyMuPDF is entirely self-contained.
3. **Pure `pip install`** — works identically on macOS, Linux, and Windows with `pip install pymupdf`. No Homebrew, apt, or other system package manager needed.

### Running the POC

```bash
uv run --no-project --with pymupdf python poc.py
```

This downloads a small public PDF and prints the first 500 characters of its first page.
