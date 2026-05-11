#!/usr/bin/env python3
"""
PIPELINE STEP: Build Chess.com Game Links Map for the Frontend
==============================================================

This script builds a small JSON map of YouTube video IDs to their corresponding
Chess.com game URLs, used by the frontend to render a "View game on Chess.com"
link beside each video card.

Purpose:
--------
The CSV files in data/csv/ pair every YouTube URL with the Chess.com game it
covers. The other pipeline steps consume the YouTube URL but discard the
Chess.com URL. This script extracts that pairing into a standalone JSON so
the frontend can resolve, for any video URL with a timestamp, the specific
Chess.com game being shown at that moment in the video.

A single YouTube video often covers multiple games (different `?t=` start
points), so each video_id maps to a list of (t, url) entries sorted by t.
The frontend looks up the entry with the largest t <= the position's
timestamp to find the game in progress at that moment.

Input:
------
- CSV files in data/csv/*.csv
  Column 0: YouTube URL (https://youtu.be/VIDEO_ID?...&t=START)
  Column 1: Game URL

Output:
-------
- JSON file: frontend/game_links.json

Format:
  {
    "VIDEO_ID": [
      { "t": 7,    "url": "https://www.chess.com/game/live/..." },
      { "t": 1234, "url": "https://www.chess.com/game/live/..." }
    ],
    ...
  }

Usage:
------
    python build_game_links_json.py

Note: This script reads only CSVs; it does not depend on the SQLite database,
so it can run before, after, or independently of the rest of the pipeline.
"""

import csv
import glob
import json
import os
import re
from urllib.parse import urlparse, parse_qs

CSV_GLOB = os.path.abspath("../../data/csv/*.csv")
OUTPUT_FILE = os.path.abspath("../../frontend/game_links.json")


def extract_video_id(url):
    m = re.search(r'youtu\.be/([^?&]+)', url)
    return m.group(1) if m else None


def extract_start_time(url):
    qs = parse_qs(urlparse(url).query)
    try:
        return int(qs.get("t", [0])[0])
    except (ValueError, TypeError):
        return 0


def main():
    by_video = {}
    skipped = 0

    for path in sorted(glob.glob(CSV_GLOB)):
        with open(path, encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) < 2: # likely title/header row
                    skipped += 1
                    continue
                yt_link, game_url = row[0].strip(), row[1].strip()
                # maybe too defensive? check if valid URL
                if not yt_link.startswith("http") or not game_url.startswith("http"):
                    print(f"[WARNING] Skipping row with non-URL value(s): {yt_link!r}, {game_url!r}")
                    skipped += 1
                    continue
                yt_video_id = extract_video_id(yt_link)
                if not yt_video_id:
                    print(f"[WARNING] Could not extract YouTube video ID from: {yt_link}")
                    skipped += 1
                    continue
                by_video.setdefault(yt_video_id, []).append({
                    "t": extract_start_time(yt_link),
                    "url": game_url,
                })

    # Sort each video's entries by start timestamp; dedupe identical (t, url)
    for yt_video_id, entries in by_video.items():
        seen = set()
        unique = []
        for e in sorted(entries, key=lambda x: x["t"]):
            key = (e["t"], e["url"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(e)
        by_video[yt_video_id] = unique

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(by_video, f, indent=2, ensure_ascii=False)

    total_pairs = sum(len(v) for v in by_video.values())
    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"[OK] Wrote {OUTPUT_FILE}")
    print(f"     Videos: {len(by_video)}")
    print(f"     Game pairs: {total_pairs}")
    print(f"     Skipped rows (headers/blanks/not processable): {skipped}")
    print(f"     File size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
