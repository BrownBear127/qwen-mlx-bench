#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import feedparser


FEED_URLS = [
    "https://hnrss.org/frontpage",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
]
REQUEST_HEADERS = {
    "User-Agent": "rss-dedupe-poc/1.0"
}
REQUEST_TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class FeedEntry:
    title: str
    normalized_title: str
    published_at: datetime


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip().casefold()


def entry_published_at(entry: feedparser.FeedParserDict) -> datetime | None:
    published = getattr(entry, "published_parsed", None)
    if not published:
        return None

    try:
        return datetime(
            published.tm_year,
            published.tm_mon,
            published.tm_mday,
            published.tm_hour,
            published.tm_min,
            published.tm_sec,
            tzinfo=timezone.utc,
        )
    except ValueError:
        return None


def fetch_feed(url: str) -> bytes:
    request = Request(url, headers=REQUEST_HEADERS)
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.read()


def collect_recent_entries(feed_url: str, cutoff: datetime) -> list[FeedEntry]:
    try:
        raw_feed = fetch_feed(feed_url)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"[warn] failed to fetch {feed_url}: {exc}", file=sys.stderr)
        return []

    parsed_feed = feedparser.parse(raw_feed)
    if getattr(parsed_feed, "bozo", False):
        exc = getattr(parsed_feed, "bozo_exception", None)
        if exc is not None:
            print(f"[warn] parsed {feed_url} with issues: {exc}", file=sys.stderr)

    recent_entries: list[FeedEntry] = []
    for entry in parsed_feed.entries:
        title = str(getattr(entry, "title", "")).strip()
        if not title:
            continue

        published_timestamp = entry_published_at(entry)
        if published_timestamp is None or published_timestamp < cutoff:
            continue

        recent_entries.append(
            FeedEntry(
                title=title,
                normalized_title=normalize_title(title),
                published_at=published_timestamp,
            )
        )

    return recent_entries


def dedupe_entries(entries: Iterable[FeedEntry]) -> list[FeedEntry]:
    unique_by_title: dict[str, FeedEntry] = {}
    for entry in sorted(entries, key=lambda item: item.published_at, reverse=True):
        unique_by_title.setdefault(entry.normalized_title, entry)
    return list(unique_by_title.values())


def main() -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    raw_entries: list[FeedEntry] = []
    for feed_url in FEED_URLS:
        raw_entries.extend(collect_recent_entries(feed_url, cutoff))

    unique_entries = dedupe_entries(raw_entries)

    print(f"raw entries: {len(raw_entries)}")
    print(f"deduped entries: {len(unique_entries)}")
    print("first 5 unique titles:")
    for entry in unique_entries[:5]:
        print(f"- {entry.title}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
