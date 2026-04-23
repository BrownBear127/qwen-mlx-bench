"""
Batch-convert a directory of Markdown files into a single EPUB ebook.

Usage:
    uv run --no-project --with ebooklib --with markdown python poc.py

Dependencies: ebooklib, markdown (see requirements.txt)
"""

import os
import glob

import markdown
from ebooklib import epub


CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chapters")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "book.epub")

BOOK_TITLE = "The Harvest Festival"
BOOK_AUTHOR = "Sample Author"
BOOK_LANG = "en"


def md_to_html(md_text: str) -> str:
    """Convert Markdown text to HTML."""
    return markdown.markdown(md_text)


def build_epub(chapter_dir: str, output_path: str) -> str:
    """Read all .md files from chapter_dir and produce a single EPUB at output_path."""
    book = epub.EpubBook()

    # Metadata
    book.set_identifier("poc-harvest-festival-001")
    book.set_title(BOOK_TITLE)
    book.set_language(BOOK_LANG)
    book.add_author(BOOK_AUTHOR)

    md_files = sorted(glob.glob(os.path.join(chapter_dir, "*.md")))
    if not md_files:
        raise FileNotFoundError(f"No .md files found in {chapter_dir}")

    chapters = []
    for i, md_path in enumerate(md_files, start=1):
        with open(md_path, encoding="utf-8") as f:
            md_text = f.read()

        html_body = md_to_html(md_text)
        filename = os.path.basename(md_path)
        chapter_id = f"chapter_{i}"

        ch = epub.EpubHtml(title=filename.replace(".md", "").replace("_", " ").title(),
                           file_name=f"{chapter_id}.xhtml",
                           lang=BOOK_LANG)
        ch.content = f"<html><body>{html_body}</body></html>"
        book.add_item(ch)
        chapters.append(ch)

    # Table of contents and spine
    book.toc = chapters
    book.spine = ["nav"] + chapters

    # Required navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(output_path, book)
    return output_path


if __name__ == "__main__":
    print(f"Source directory : {CHAPTERS_DIR}")
    out = build_epub(CHAPTERS_DIR, OUTPUT_FILE)
    size = os.path.getsize(out)
    print(f"Output file      : {out}")
    print(f"Size             : {size:,} bytes ({size / 1024:.1f} KB)")
