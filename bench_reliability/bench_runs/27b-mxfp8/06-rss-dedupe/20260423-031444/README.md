# RSS Feed Aggregator POC

A minimal proof-of-concept that fetches 3 technology RSS feeds, filters entries
from the last 24 hours, deduplicates by normalized title, and prints a summary.

## Feeds

| # | Source | URL |
|---|--------|-----|
| 1 | Hacker News | https://hnrss.org/frontpage |
| 2 | The Verge | https://www.theverge.com/rss/index.xml |
| 3 | Ars Technica | https://feeds.arstechnica.com/arstechnica/index |

## How it works

1. **Fetch** each RSS feed using `feedparser`.
2. **Filter** entries published within the last 24 hours (UTC).
3. **Deduplicate** entries whose titles match after normalizing (lowercase,
   whitespace collapsed).
4. **Print** the raw/deduped counts and the first 5 unique titles.

## Requirements

- Python 3.8+
- `feedparser` (listed in `requirements.txt`)

## Running

```bash
# Install dependencies (if not using uv --with)
pip install -r requirements.txt

# Run with uv (recommended)
uv run --no-project --with feedparser python poc.py

# Or run directly if feedparser is installed
python poc.py
```

## Error handling

Network errors on individual feeds are caught and logged as warnings — they do
not crash the entire POC.
