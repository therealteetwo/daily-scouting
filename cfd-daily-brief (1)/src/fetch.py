"""Fetch news items from RSS feeds and Google News queries."""

import hashlib
import time
import urllib.parse
from datetime import datetime, timedelta, timezone

import feedparser

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CFDBrief/1.0)"}


def _entry_time(entry):
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
    return None


def _parse_feed(url, source, cutoff):
    items = []
    try:
        feed = feedparser.parse(url, request_headers=HEADERS)
        for e in feed.entries:
            ts = _entry_time(e)
            if ts is not None and ts < cutoff:
                continue  # too old
            items.append({
                "source": source,
                "title": (e.get("title") or "").strip(),
                "link": e.get("link", ""),
                "summary": (e.get("summary") or "")[:500],
                "published": ts.isoformat() if ts else "unknown",
            })
    except Exception as exc:  # a dead feed must never kill the brief
        print(f"[warn] feed failed: {source} ({url}): {exc}")
    return items


def fetch_all(config):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.get("lookback_hours", 26))
    items = []

    # 1. Direct RSS feeds
    for feed in config.get("rss_feeds", []):
        items += _parse_feed(feed["url"], feed["name"], cutoff)

    # 2. Google News: one query per competitor
    comp = config.get("competitors", {})
    for tier, names in comp.items():
        for name in names:
            q = urllib.parse.quote(f'"{name}"')
            url = GOOGLE_NEWS_RSS.format(q=q)
            for it in _parse_feed(url, f"GoogleNews:{name}", cutoff):
                it["competitor"] = name
                it["tier"] = tier
                items.append(it)

    # 3. Google News: industry topic queries
    for query in config.get("topic_queries", []):
        q = urllib.parse.quote(query)
        items += _parse_feed(GOOGLE_NEWS_RSS.format(q=q), f"GoogleNews:{query}", cutoff)

    # Dedupe by normalized title
    seen, unique = set(), []
    for it in items:
        key = hashlib.md5(it["title"].lower().strip().encode()).hexdigest()
        if key not in seen and it["title"]:
            seen.add(key)
            unique.append(it)

    # Cap for cost control — competitor-tagged items get priority
    unique.sort(key=lambda x: (0 if x.get("competitor") else 1))
    max_items = config.get("max_items", 60)
    print(f"[info] fetched {len(items)} items, {len(unique)} unique, keeping {min(len(unique), max_items)}")
    return unique[:max_items]
