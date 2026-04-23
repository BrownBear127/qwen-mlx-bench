"""
Minimal POC: download a small public-domain PDF and print the first 500
characters of text extracted from its first page only.

Usage:
    uv run --no-project --with pypdf python poc.py
"""

import tempfile
import urllib.request

from pypdf import PdfReader

# A small public PDF test file (~20 KB).
PDF_URL = "https://www.orimi.com/pdf-test.pdf"


def main() -> None:
    # 1. Download the PDF into a temporary file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        urllib.request.urlretrieve(PDF_URL, tmp.name)
        path = tmp.name

    # 2. Extract text from the first page only
    reader = PdfReader(path)
    first_page = reader.pages[0]
    text = first_page.extract_text() or ""

    # 3. Print exactly the first 500 characters (no more, no less)
    print(text[:500])


if __name__ == "__main__":
    main()
