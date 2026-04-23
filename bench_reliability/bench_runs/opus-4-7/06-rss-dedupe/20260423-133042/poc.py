"""Minimal RSS feed deduplication POC."""

import re
import time
from datetime import datetime, timezone

import feedparser

FEEDS = [
    "https://hnrss.org/frontpage",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
]

TWENTY_FOUR_HOURS_AGO = datetime.now(timezone.utc).timestamp() - 86400


def normalize_title(title: str) -> str:
    """Lowercase and collapse whitespace."""
    return re.sub(r"\s+", " ", title.strip().lower())


def fetch_recent_entries(url: str) -> list[dict]:
    """Fetch a single feed and return entries from the last 24 hours."""
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"  [error] {url}: {e}")
        return []

    if feed.bozo and not feed.entries:
        print(f"  [warn] {url}: {feed.bozo_exception}")
        return []

    entries = []
    for entry in feed.entries:
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if not published:
            continue
        ts = time.mktime(published) - time.timezone  # convert struct_time (UTC) to epoch
        if ts >= TWENTY_FOUR_HOURS_AGO:
            entries.append({
                "title": entry.get("title", "(no title)"),
                "link": entry.get("link", ""),
                "published": ts,
            })
    return entries


def main():
    all_entries = []
    for url in FEEDS:
        print(f"Fetching {url} ...")
        entries = fetch_recent_entries(url)
        print(f"  -> {len(entries)} recent entries")
        all_entries.extend(entries)

    seen: set[str] = set()
    unique: list[dict] = []
    for entry in all_entries:
        key = normalize_title(entry["title"])
        if key not in seen:
            seen.add(key)
            unique.append(entry)

    print(f"\nRaw entries (last 24h): {len(all_entries)}")
    print(f"Deduped entries:        {len(unique)}")
    print(f"\nFirst 5 unique titles:")
    for i, entry in enumerate(unique[:5], 1):
        print(f"  {i}. {entry['title']}")


if __name__ == "__main__":
    main()
