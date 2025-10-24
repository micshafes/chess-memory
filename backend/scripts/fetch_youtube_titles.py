"""
Fetch YouTube video titles using oEmbed API (no API key required)
and update the database to include video metadata.
"""

import sqlite3
import json
import requests
from urllib.parse import urlparse, parse_qs
import time
import os

# === CONFIG ===
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    # Handle youtu.be URLs
    if 'youtu.be' in url:
        parsed = urlparse(url)
        return parsed.path.lstrip('/')
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
    Returns the video title or None if request fails.
    """
    if not video_id:
        return None
    
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    
    try:
        response = requests.get(oembed_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('title')
    except Exception as e:
        print(f"[ERROR] Error fetching title for {video_id}: {e}")
    
    return None

def main():
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # Add new column for video metadata if it doesn't exist
    try:
        cur.execute("""
            ALTER TABLE positions 
            ADD COLUMN video_metadata TEXT DEFAULT '[]'
        """)
        conn.commit()
        print("[OK] Added video_metadata column to database")
    except sqlite3.OperationalError:
        print("[INFO] video_metadata column already exists")
    
    # Get all positions with videos
    cur.execute("SELECT fen, video_links FROM positions WHERE video_links != '[]'")
    rows = cur.fetchall()
    
    print(f"\n[INFO] Found {len(rows)} positions with videos")
    print("[INFO] Fetching YouTube titles...\n")
    
    # Track unique video IDs to avoid duplicate API calls
    video_cache = {}
    total_updated = 0
    
    for idx, (fen, video_links_json) in enumerate(rows, 1):
        video_urls = json.loads(video_links_json)
        video_metadata = []
        
        for url in video_urls:
            video_id = extract_video_id(url)
            
            # Check cache first
            if video_id in video_cache:
                title = video_cache[video_id]
            else:
                # Fetch from API
                title = get_youtube_title(video_id)
                video_cache[video_id] = title
                
                # Be nice to YouTube's servers
                time.sleep(0.1)
            
            video_metadata.append({
                "url": url,
                "video_id": video_id,
                "title": title if title else "Danya's Chess Speedrun"
            })
        
        # Update database
        cur.execute(
            "UPDATE positions SET video_metadata = ? WHERE fen = ?",
            (json.dumps(video_metadata), fen)
        )
        
        if idx % 100 == 0:
            conn.commit()
            print(f"  Progress: {idx}/{len(rows)} positions processed...")
    
    conn.commit()
    conn.close()
    
    print(f"\n[OK] Successfully updated {len(rows)} positions!")
    print(f"[INFO] Cached {len(video_cache)} unique video titles")

if __name__ == "__main__":
    main()

