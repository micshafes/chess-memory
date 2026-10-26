#!/usr/bin/env python3
"""
OPTIONAL: Fetch YouTube View Counts
===================================

Fetches the current view count of every video in the database so the frontend
can list the most popular videos first.

Purpose:
--------
View counts change over time, so they are kept in their own small file with the
date they were fetched, instead of inside the position database. Re-run this
script whenever you want fresher numbers, then re-run step 5 to export them.

Input:
------
- SQLite database (data/sqlite/chess_positions.db) with video_links column

Output:
-------
- JSON file: data/json/video_view_counts.json
  {
    "fetched_at": "2026-10-26T15:30:00Z",
    "source": "yt-dlp",
    "view_counts": {"VIDEO_ID": 123456, ...}
  }

Requirements:
-------------
    pip install yt-dlp

Usage:
------
    python fetch_view_counts.py
    python 5_export_to_frontend_json.py

Videos that fail to fetch keep their previous count (if any), so a partial
run never loses data.
"""

import json
import os
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlparse

from yt_dlp import YoutubeDL

# === CONFIGURATION ===
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")
OUTPUT_FILE = os.path.abspath("../../data/json/video_view_counts.json")
MAX_WORKERS = 4
RETRIES = 1  # YouTube sometimes rejects a request; one retry usually works


def extract_video_id(url):
    """
    Extract the YouTube video ID from a youtu.be or youtube.com URL.

    Args:
        url: YouTube URL string

    Returns:
        Video ID string, or None if it is not a YouTube URL
    """
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/") or None
    if "youtube.com" in parsed.netloc and parsed.path == "/watch":
        for part in parsed.query.split("&"):
            if part.startswith("v="):
                return part[2:]
    return None


def fetch_view_count(video_id):
    """
    Fetch the current view count of one video with yt-dlp (no API key needed).

    Args:
        video_id: YouTube video ID

    Returns:
        Tuple of (video_id, view count int or None on failure)
    """
    options = {"quiet": True, "no_warnings": True, "skip_download": True}
    for attempt in range(1, RETRIES + 2):
        try:
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}",
                    download=False,
                    process=False,
                )
            return video_id, info.get("view_count")
        except Exception as e:  # yt-dlp raises many error types
            print(f"[WARNING] Attempt {attempt} failed for {video_id}: {e}")
            time.sleep(2)
    return video_id, None


def main():
    """
    Collect all video IDs from the database, fetch their view counts and save
    them with a timestamp.
    """
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT video_links FROM positions").fetchall()
    conn.close()

    video_ids = set()
    for (links_json,) in rows:
        for url in json.loads(links_json or "[]"):
            video_id = extract_video_id(url)
            if video_id:
                video_ids.add(video_id)
    print(f"[INFO] Fetching view counts for {len(video_ids)} videos...")

    # Keep previous counts so failed fetches don't erase data
    view_counts = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            view_counts = json.load(f).get("view_counts", {})

    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    failed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for video_id, count in pool.map(fetch_view_count, sorted(video_ids)):
            if count is None:
                failed += 1
            else:
                view_counts[video_id] = count

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "fetched_at": fetched_at,
                "source": "yt-dlp",
                "view_counts": dict(sorted(view_counts.items())),
            },
            f,
            indent=2,
        )

    print(f"[OK] Saved {len(view_counts)} view counts to {OUTPUT_FILE}")
    if failed:
        print(f"[WARNING] {failed} videos failed (previous counts kept)")


if __name__ == "__main__":
    main()
