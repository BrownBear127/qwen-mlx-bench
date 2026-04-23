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
    """Lowercase and collapse all whitespace to single spaces."""
    return re.sub(r"\s+", " ", title.strip().lower())


def fetch_feed(url: str):
    """Fetch and parse a single RSS feed. Returns the feed object or None on error."""
    try:
        return feedparser.parse(url)
    except Exception as exc:
        print(f"[WARN] Failed to fetch {url}: {exc}")
        return None


def entries_from_last_24h(feed):
    """Return entries published within the last 24 hours (UTC)."""
    if feed is None:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    results = []

    for entry in feed.entries:
        # feedparser normalizes dates into a datetime via published_parsed
        published = getattr(entry, "published_parsed", None)
        if published is None:
            continue
        # Convert the time.struct_time to a timezone-aware datetime (assumed UTC)
        entry_dt = datetime(*published[:6], tzinfo=timezone.utc)
        if entry_dt >= cutoff:
            results.append(entry)

    return results


def main():
    all_entries = []
    for url in FEEDS:
        feed = fetch_feed(url)
        recent = entries_from_last_24h(feed)
        print(f"[{url}] -> {len(recent)} entries in last 24h")
        all_entries.extend(recent)

    raw_count = len(all_entries)

    # Deduplicate by normalized title — keep first occurrence
    seen: set[str] = set()
    deduped: list = []
    for entry in all_entries:
        key = normalize_title(entry.get("title", ""))
        if key not in seen:
            seen.add(key)
            deduped.append(entry)

    deduped_count = len(deduped)

    print(f"\nCounts: raw={raw_count}, deduped={deduped_count}")
    print("\nFirst 5 unique titles:")
    for i, entry in enumerate(deduped[:5], 1):
        print(f"  {i}. {entry.get('title', '(no title)')}")


if __name__ == "__main__":
    main()
