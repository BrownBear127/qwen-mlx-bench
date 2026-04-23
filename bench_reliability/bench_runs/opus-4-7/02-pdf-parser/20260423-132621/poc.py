"""Minimal POC: download a public-domain PDF and print first 500 chars of page 1."""

import urllib.request
import tempfile
import os

import pymupdf  # PyMuPDF

# A small, freely available PDF hosted by the US government (public domain).
PDF_URL = "https://unec.edu.az/application/uploads/2014/12/pdf-sample.pdf"


def main():
    # Download PDF to a temp file, adding a User-Agent to avoid 403s
    req = urllib.request.Request(PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
    tmp_path = tempfile.mktemp(suffix=".pdf")
    try:
        with urllib.request.urlopen(req) as resp, open(tmp_path, "wb") as f:
            f.write(resp.read())
        doc = pymupdf.open(tmp_path)
        page = doc[0]
        text = page.get_text()
        doc.close()
        # Print exactly the first 500 characters
        print(text[:500])
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    main()
