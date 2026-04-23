# RSS Feed POC

Minimal proof-of-concept that fetches 3 RSS feeds, filters entries from the
last 24 hours, deduplicates by normalized title, and prints summary statistics.

## Dependencies

| Package    | Purpose                        |
|------------|--------------------------------|
| feedparser | Robust RSS / Atom feed parser |

Install via:

```bash
pip install -r requirements.txt
```

## Usage

```bash
uv run --no-project --with feedparser python poc.py
```

## What it does

1. **Fetches** three RSS feeds (Hacker News, The Verge, Ars Technica).
2. **Filters** entries published within the last 24 hours (using `published_parsed`
   or `updated_parsed` from feedparser).
3. **Deduplicates** entries whose titles match after normalization
   (case-insensitive, whitespace collapsed).
4. **Prints** the count of raw vs deduped entries and the first 5 unique titles.

Network errors on individual feeds are caught and logged as warnings — they do not
crash the program.
