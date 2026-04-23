"""Minimal POC: fetch 3 RSS feeds, filter last 24h, deduplicate, print stats."""

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
    """Fetch and parse a single RSS feed. Returns entries list or empty on error."""
    try:
        feed = feedparser.parse(url)
        return feed.entries
    except Exception as exc:
        print(f"  [WARN] Failed to fetch {url}: {exc}")
        return []


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    all_entries = []

    for url in FEEDS:
        print(f"Fetching {url} ...")
        entries = fetch_feed(url)
        for entry in entries:
            # feedparser normalizes dates to time.struct_time (UTC)
            published = getattr(entry, "published_parsed", None)
            if published is None:
                published = getattr(entry, "updated_parsed", None)
            if published is None:
                continue
            entry_dt = datetime(*published[:6], tzinfo=timezone.utc)
            if entry_dt >= cutoff:
                all_entries.append(entry)

    raw_count = len(all_entries)

    # Deduplicate by normalized title, keeping the first occurrence
    seen: set[str] = set()
    deduped: list[dict] = []
    for entry in all_entries:
        key = normalize_title(entry.title)
        if key not in seen:
            seen.add(key)
            deduped.append(entry)

    deduped_count = len(deduped)

    print(f"\nCounts: raw={raw_count}, deduped={deduped_count}")
    print(f"\nFirst {min(5, deduped_count)} unique titles:")
    for i, entry in enumerate(deduped[:5], 1):
        print(f"  {i}. {entry.title}")


if __name__ == "__main__":
    main()
