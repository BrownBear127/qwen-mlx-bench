"""
Minimal POC: Extract text from the first page of a public-domain PDF
using pypdf (pure-Python, cross-platform library).
"""

import urllib.request
import tempfile
import os

from pypdf import PdfReader

# A small public test PDF (20 KB)
PDF_URL = "https://www.orimi.com/pdf-test.pdf"
OUTPUT_LIMIT = 500  # print exactly 500 chars


def download_pdf(url: str) -> str:
    """Download a PDF from a URL and return the local file path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        urllib.request.urlretrieve(url, tmp.name)
    except Exception:
        os.unlink(tmp.name)
        raise
    return tmp.name


def main():
    pdf_path = download_pdf(PDF_URL)
    try:
        reader = PdfReader(pdf_path)
        first_page = reader.pages[0]
        text = first_page.extract_text() or ""

        # Print exactly 500 characters (no more, no less)
        print(text[:OUTPUT_LIMIT])
    finally:
        os.unlink(pdf_path)


if __name__ == "__main__":
    main()
