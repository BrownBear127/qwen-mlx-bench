#!/usr/bin/env python3
"""
Minimal POC: Fetch 3 RSS feeds, filter entries from the last 24 hours,
deduplicate by normalized title, and print summary stats.
"""

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


def fetch_feed(url: str):
    """Parse a single RSS feed. Returns the feed object or None on error."""
    try:
        return feedparser.parse(url)
    except Exception as exc:
        print(f"  [WARN] Failed to fetch {url}: {exc}")
        return None


def main():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)

    raw_entries = []
    for url in FEEDS:
        feed = fetch_feed(url)
        if feed is None:
            continue
        for entry in feed.entries:
            # feedparser normalizes dates into parsed (UTC) datetime
            pub = getattr(entry, "published_parsed", None)
            if pub is None:
                pub = getattr(entry, "updated_parsed", None)
            if pub is None:
                continue
            # Convert the time tuple to a datetime
            try:
                pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
            if pub_dt >= cutoff:
                raw_entries.append(entry)

    # Deduplicate by normalized title (first occurrence wins)
    seen: set[str] = set()
    deduped: list = []
    for entry in raw_entries:
        key = normalize_title(entry.title)
        if key not in seen:
            seen.add(key)
            deduped.append(entry)

    print(f"Raw entries (last 24h): {len(raw_entries)}")
    print(f"Deduped entries:         {len(deduped)}")
    print()
    print("First 5 unique titles:")
    for i, entry in enumerate(deduped[:5], 1):
        print(f"  {i}. {entry.title}")


if __name__ == "__main__":
    main()
