from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import feedparser
import pandas as pd


def ingest_rss_config(config_path: str | Path) -> pd.DataFrame:
    """
    Read a JSON list of RSS sources and return a normalised dataframe.

    Expected source object:
    {
      "name": "Example regulator",
      "url": "https://example.com/feed.xml",
      "source_type": "regulator",
      "market": "Germany"
    }

    Feed availability and website terms can change. Use only permitted public feeds.
    """
    sources: list[dict[str, Any]] = json.loads(Path(config_path).read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []

    for source in sources:
        parsed = feedparser.parse(source["url"])
        for entry in parsed.entries:
            records.append({
                "published_at": entry.get("published", entry.get("updated", "")),
                "source": source["name"],
                "source_type": source.get("source_type", "media"),
                "market": source.get("market", "Europe"),
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "url": entry.get("link", ""),
            })

    df = pd.DataFrame(records)
    if not df.empty:
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
        df = df.dropna(subset=["published_at"]).copy()
        df["published_at"] = df["published_at"].dt.tz_convert(None)
    return df
