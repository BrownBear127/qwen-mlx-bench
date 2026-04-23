# RSS Dedupe POC

This POC uses `feedparser` to parse three RSS feeds, keeps only entries whose `published` time is within the last 24 hours, deduplicates entries by normalized title, and prints:

- the raw entry count
- the deduped entry count
- the first 5 unique titles

## Files

- `poc.py`: runnable script
- `requirements.txt`: pinned dependency for verifier installs

## Run

```bash
uv run --no-project --with feedparser==6.0.12 python poc.py
```

If a single feed cannot be fetched, the script prints a warning to stderr and continues with the remaining feeds.

## Title normalization

Deduplication treats titles as the same when:

- letter case differs
- repeated whitespace differs

Examples:

- `Hello   World`
- `hello world`

These normalize to the same dedupe key.
