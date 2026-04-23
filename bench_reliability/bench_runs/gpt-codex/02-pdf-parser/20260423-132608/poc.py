from io import BytesIO
import sys
from urllib.request import Request, urlopen

from pypdf import PdfReader


PDF_URL = "https://ntrs.nasa.gov/api/citations/19790016570/downloads/19790016570.pdf"


def download_pdf_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def extract_first_page_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    if not reader.pages:
        raise ValueError("The PDF has no pages.")
    return reader.pages[0].extract_text() or ""


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def main() -> None:
    pdf_bytes = download_pdf_bytes(PDF_URL)
    first_page_text = extract_first_page_text(pdf_bytes)
    normalized_text = normalize_whitespace(first_page_text)

    if len(normalized_text) < 500:
        raise ValueError("The first page contains fewer than 500 characters after normalization.")

    sys.stdout.write(normalized_text[:500])


if __name__ == "__main__":
    main()
