# RSS Feed POC

A minimal proof-of-concept that fetches three technology RSS feeds, filters entries from the last 24 hours, deduplicates by normalized title, and reports results.

## Feeds

- Hacker News frontpage (`hnrss.org`)
- The Verge
- Ars Technica

## Requirements

- Python 3.9+
- `feedparser` (listed in `requirements.txt`)

## Usage

```bash
uv run --no-project --with feedparser python poc.py
```

## Output

Prints:
1. The count of raw entries and deduplicated entries.
2. The first 5 unique titles.

## How it works

1. **Fetches** each RSS feed via `feedparser.parse()`. Network errors on individual feeds are caught and skipped — one failing feed won't crash the POC.
2. **Filters** entries to the last 24 hours using the entry's `published_parsed` / `updated_parsed` / `created_parsed` timestamp.
3. **Deduplicates** by normalizing titles (lowercased, whitespace collapsed) and keeping only the first occurrence of each unique title.
4. **Reports** the raw/deduped counts and the first 5 unique titles.
