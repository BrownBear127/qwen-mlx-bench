# RSS Feed Aggregator POC

A minimal proof-of-concept that fetches three tech-news RSS feeds, filters entries from the last 24 hours, deduplicates by normalized title, and prints summary statistics.

## Feeds

- Hacker News Front Page (`hnrss.org`)
- The Verge
- Ars Technica

## Requirements

- Python 3.8+
- `feedparser` (listed in `requirements.txt`)

## Usage

```bash
uv run --no-project --with feedparser python poc.py
```

## How it works

1. **Fetches** each RSS feed via `feedparser.parse()`. Network errors on individual feeds are caught and skipped — they won't crash the whole POC.
2. **Filters** entries to only those published within the last 24 hours (UTC).
3. **Deduplicates** entries whose titles match after lowercasing and collapsing whitespace.
4. **Prints** the raw entry count, deduplicated count, and the first 5 unique titles.
