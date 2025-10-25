#!/usr/bin/env python3
"""
STEP 3: Fetch YouTube Video Titles
===================================

This script enriches the database with actual YouTube video titles using YouTube's oEmbed API.

Purpose:
--------
The database initially only stores YouTube URLs. This script fetches the real video titles
(e.g., "1200 Speedrun - Part 23: Crushing the Caro-Kann") using YouTube's oEmbed API,
which doesn't require an API key.

This makes the frontend much more user-friendly by showing descriptive video titles
instead of generic "Danya's Chess Speedrun" labels.

Input:
------
- SQLite database (data/sqlite/chess_positions.db) with video_links column

Output:
-------
- Updates database with new video_metadata column containing JSON:
  [
    {
      "url": "https://youtu.be/VIDEO_ID?t=123",
      "video_id": "VIDEO_ID",
      "title": "Actual YouTube video title"
    },
    ...
  ]

API Details:
------------
- Uses YouTube oEmbed API: https://www.youtube.com/oembed
- No API key required
- Rate limit: ~100 requests/second (we add 0.1s delay to be safe)
- Returns video metadata including title, author, thumbnail URL

Usage:
------
    python 3_fetch_youtube_titles.py
    
Note: This script can take several minutes to complete for large databases.
Progress is saved every 100 positions, so it's safe to interrupt and restart.
"""

import sqlite3
import json
import requests
from urllib.parse import urlparse, parse_qs
import time
import os

# === CONFIGURATION ===
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")


def extract_video_id(url):
    """
    Extract YouTube video ID from various URL formats.
    
    Supports both formats:
    - https://youtu.be/VIDEO_ID?t=123
    - https://www.youtube.com/watch?v=VIDEO_ID&t=123
    
    Args:
        url: YouTube URL string
        
    Returns:
        Video ID string, or None if extraction fails
        
    Examples:
        extract_video_id("https://youtu.be/dQw4w9WgXcQ?t=42") -> "dQw4w9WgXcQ"
        extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") -> "dQw4w9WgXcQ"
    """
    # Handle youtu.be short URLs
    if 'youtu.be' in url:
        parsed = urlparse(url)
        video_id = parsed.path.lstrip('/')
        # Remove query parameters from video ID if present
        return video_id.split('?')[0]
    
    # Handle youtube.com URLs
    elif 'youtube.com' in url:
        parsed = urlparse(url)
        if parsed.path == '/watch':
            qs = parse_qs(parsed.query)
            return qs.get('v', [None])[0]
    
    return None


def get_youtube_title(video_id):
    """
    Fetch video title using YouTube oEmbed API (no API key needed).
    
    The oEmbed API is designed for embedding videos and provides basic metadata
    without authentication. This is perfect for our use case.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Video title string, or None if request fails
        
    API Response Example:
        {
          "title": "Daniel Naroditsky Speedrun to 3000",
          "author_name": "Daniel Naroditsky",
          "author_url": "https://www.youtube.com/@DanielNaroditskyGM",
          "type": "video",
          "height": 270,
          "width": 480,
          "version": "1.0",
          "provider_name": "YouTube",
          "provider_url": "https://www.youtube.com/",
          "thumbnail_height": 360,
          "thumbnail_width": 480,
          "thumbnail_url": "https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg",
          "html": "<iframe width=\"480\" height=\"270\" ...></iframe>"
        }
    """
    if not video_id:
        return None
    
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    
    try:
        response = requests.get(oembed_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('title')
        elif response.status_code == 404:
            print(f"[WARNING] Video not found or private: {video_id}")
            return None
        else:
            print(f"[ERROR] Unexpected status {response.status_code} for {video_id}")
            return None
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout fetching title for {video_id}")
        return None
    except Exception as e:
        print(f"[ERROR] Error fetching title for {video_id}: {e}")
        return None


def main():
    """
    Main function to fetch YouTube titles and update database.
    
    Process:
    1. Add video_metadata column to database if not exists
    2. Fetch all positions with video links
    3. For each video URL, extract video ID and fetch title
    4. Cache titles to avoid duplicate API calls
    5. Update database with enriched metadata
    """
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # === ADD COLUMN IF NOT EXISTS ===
    try:
        cur.execute("""
            ALTER TABLE positions 
            ADD COLUMN video_metadata TEXT DEFAULT '[]'
        """)
        conn.commit()
        print("[OK] Added video_metadata column to database")
    except sqlite3.OperationalError:
        print("[INFO] video_metadata column already exists")
    
    # === FETCH POSITIONS WITH VIDEOS ===
    cur.execute("SELECT fen, video_links FROM positions WHERE video_links != '[]'")
    rows = cur.fetchall()
    
    print(f"\n[INFO] Found {len(rows)} positions with videos")
    print("[INFO] Fetching YouTube titles...")
    print("[INFO] This may take a few minutes...\n")
    
    # === PROCESS EACH POSITION ===
    # Track unique video IDs to avoid duplicate API calls
    video_cache = {}
    total_updated = 0
    cache_hits = 0
    
    for idx, (fen, video_links_json) in enumerate(rows, 1):
        video_urls = json.loads(video_links_json)
        video_metadata = []
        
        # Process each video URL for this position
        for url in video_urls:
            video_id = extract_video_id(url)
            
            if not video_id:
                print(f"[WARNING] Could not extract video ID from: {url}")
                video_metadata.append({
                    "url": url,
                    "video_id": None,
                    "title": "Danya's Chess Speedrun"
                })
                continue
            
            # Check cache first to avoid duplicate API calls
            if video_id in video_cache:
                title = video_cache[video_id]
                cache_hits += 1
            else:
                # Fetch from YouTube API
                title = get_youtube_title(video_id)
                video_cache[video_id] = title
                
                # Be respectful to YouTube's servers - add small delay
                time.sleep(0.1)
            
            # Add to metadata list with fallback title
            video_metadata.append({
                "url": url,
                "video_id": video_id,
                "title": title if title else "Danya's Chess Speedrun"
            })
        
        # === UPDATE DATABASE ===
        cur.execute(
            "UPDATE positions SET video_metadata = ? WHERE fen = ?",
            (json.dumps(video_metadata), fen)
        )
        
        # Commit every 100 positions for progress safety
        if idx % 100 == 0:
            conn.commit()
            print(f"  Progress: {idx}/{len(rows)} positions processed...")
            print(f"  Cache hits: {cache_hits} | API calls: {len(video_cache)}")
    
    # Final commit
    conn.commit()
    conn.close()
    
    # === SUMMARY ===
    print(f"\n{'='*60}")
    print(f"[OK] Successfully updated {len(rows)} positions!")
    print(f"[INFO] Cached {len(video_cache)} unique video titles")
    print(f"[INFO] Cache hit rate: {(cache_hits / max(1, cache_hits + len(video_cache))) * 100:.1f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

