# PDF parser POC

This POC uses `pypdf`.

## Why this library fits macOS and Linux

`pypdf` is a pure Python package, so it does not rely on macOS-only frameworks, native system binaries, or shell commands. Its PyPI metadata also marks it as `Operating System :: OS Independent`, and the published wheel is `py3-none-any`, which means the same package works across platforms supported by Python.

References:

- PyPI: https://pypi.org/project/pypdf/
- Documentation: https://pypdf.readthedocs.io/

## Why this PDF is acceptable

The script downloads a public PDF from NASA Technical Reports Server:

- Source page: https://ntrs.nasa.gov/citations/19790016570
- Download URL used by the script: https://ntrs.nasa.gov/api/citations/19790016570/downloads/19790016570.pdf

The source page states: `Copyright: Work of the US Gov. Public Use Permitted.`

## Run

```bash
uv run --no-project --with pypdf==6.8.0 python poc.py
```

## What it prints

Exactly the first 500 characters of the extracted text from page 1, after collapsing repeated whitespace into single spaces.
