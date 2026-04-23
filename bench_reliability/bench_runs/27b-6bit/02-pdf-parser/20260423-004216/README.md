# PDF Text Extraction POC

## Library Choice: `pypdf`

**`pypdf`** is a **pure-Python** PDF library — it has **zero C extensions** and **zero system-level dependencies**. This makes it fully cross-platform compatible on both **macOS** and **Linux** (and Windows) without any platform-specific build steps, native libraries, or system commands.

### Why `pypdf` is cross-platform compatible

| Criterion | Detail |
|---|---|
| **Pure Python** | The entire codebase is written in Python. No `.so`/`.dylib`/`.dll` files are compiled or loaded. |
| **No system commands** | It does not invoke `pdftotext`, `qpdf`, or any external CLI tools. |
| **No macOS-only deps** | It does not depend on `CoreGraphics`, `Quartz`, or any Apple-framework bindings. |
| **No Linux-only deps** | It does not depend on `poppler`, `libreoffice`, or any distro-specific packages. |
| **Pre-built wheels** | Available on PyPI for all major platforms via `pip`/`uv`. |

## How to Run

```bash
uv run --no-project --with pypdf python poc.py
```

This downloads a public-domain PDF (Alice in Wonderland, 1865 first edition) from Adobe's servers, extracts the text from its first page, and prints exactly the first 500 characters.

## Files

- `poc.py` — the proof-of-concept script
- `requirements.txt` — third-party dependency list (just `pypdf`)
