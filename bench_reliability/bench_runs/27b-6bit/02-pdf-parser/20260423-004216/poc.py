"""Minimal POC: extract text from the first page of a public-domain PDF.

Usage:
    uv run --no-project --with pypdf python poc.py
"""

import tempfile
import urllib.request

from pypdf import PdfReader

PDF_URL = "https://www.adobe.com/be_en/active-use/pdf/Alice_in_Wonderland.pdf"
MAX_CHARS = 500


def main() -> None:
    # Download the PDF into a temporary file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        urllib.request.urlretrieve(PDF_URL, tmp.name)
        tmp_path = tmp.name

    # Read the first page only
    reader = PdfReader(tmp_path)
    first_page = reader.pages[0]
    text = first_page.extract_text() or ""

    # Print exactly the first 500 characters
    print(text[:MAX_CHARS])


if __name__ == "__main__":
    main()
