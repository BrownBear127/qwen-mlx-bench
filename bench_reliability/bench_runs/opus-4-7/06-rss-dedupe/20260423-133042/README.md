# RSS Feed Deduplication POC

Fetches entries from three RSS feeds (Hacker News, The Verge, Ars Technica), filters to the last 24 hours, deduplicates by normalized title, and prints a summary.

## Requirements

- Python 3.10+
- [feedparser](https://pypi.org/project/feedparser/)

## Usage

```bash
uv run --no-project --with feedparser python poc.py
```

Or with pip:

```bash
pip install -r requirements.txt
python poc.py
```

## How deduplication works

Titles are normalized by lowercasing and collapsing all whitespace sequences to a single space. Entries with identical normalized titles are considered duplicates; only the first occurrence is kept.
