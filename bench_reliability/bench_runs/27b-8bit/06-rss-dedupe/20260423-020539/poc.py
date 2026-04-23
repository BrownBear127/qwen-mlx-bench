#!/usr/bin/env python3
"""Minimal POC: fetch 3 RSS feeds, filter last 24h, deduplicate, report."""

import re
from datetime import datetime, timedelta, timezone

import feedparser


FEEDS = [
    "https://hnrss.org/frontpage",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
]


def normalize_title(title: str) -> str:
    """Case-insensitive, whitespace-collapsed title for deduplication."""
    return re.sub(r"\s+", " ", title.strip().lower())


def parse_timestamp(entry) -> datetime | None:
    """Extract a UTC datetime from an RSS entry, trying common fields."""
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            return datetime(*parsed[:6], tzinfo=timezone.utc)
    return None


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    all_entries: list[tuple[str, str]] = []  # (normalized_title, original_title)

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            print(f"  [WARN] Failed to fetch {url}: {exc}")
            continue

        for entry in feed.entries:
            ts = parse_timestamp(entry)
            if ts is None or ts < cutoff:
                continue
            title = entry.get("title", "")
            all_entries.append((normalize_title(title), title))

    raw_count = len(all_entries)

    # Deduplicate preserving first occurrence
    seen: set[str] = set()
    unique: list[str] = []
    for norm, orig in all_entries:
        if norm not in seen:
            seen.add(norm)
            unique.append(orig)

    deduped_count = len(unique)

    print(f"Entries (raw, deduped): ({raw_count}, {deduped_count})")
    print("First 5 unique titles:")
    for i, title in enumerate(unique[:5], 1):
        print(f"  {i}. {title}")


if __name__ == "__main__":
    main()
