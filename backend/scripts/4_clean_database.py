#!/usr/bin/env python3
"""
STEP 4: Clean Database of Invalid Links
========================================

This script removes Chess.com game URLs that were accidentally added to video_links.

Purpose:
--------
During data processing, sometimes Chess.com game URLs get mixed into the video_links field.
This utility script cleans them out, keeping only YouTube video URLs.

This is a safety/maintenance script that ensures data quality.

Input/Output:
-------------
- Modifies: data/sqlite/chess_positions.db (in-place)
- Updates: video_links column to remove any Chess.com URLs

Detection:
----------
Removes any links matching the pattern:
    https?://(www\.)?chess\.com/game/live/\d+

Usage:
------
    python 4_clean_database.py
"""

import sqlite3
import json
import re
import os

# === CONFIGURATION ===
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")

# Regex pattern to detect Chess.com game URLs
# Matches: http://chess.com/game/live/123456 or https://www.chess.com/game/live/123456
CHESS_URL_PATTERN = re.compile(r"https?://(www\.)?chess\.com/game/live/\d+")


def main():
    """
    Main function to clean Chess.com URLs from video_links.
    
    Process:
    1. Connect to database
    2. Fetch all positions with video_links
    3. Filter out Chess.com URLs from each position's video_links
    4. Update database if any links were removed
    """
    print("="*60)
    print("DATABASE CLEANUP: Removing Chess.com URLs")
    print("="*60)
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # === FETCH ALL POSITIONS ===
    cur.execute("SELECT fen, video_links FROM positions")
    rows = cur.fetchall()
    
    print(f"\n[INFO] Checking {len(rows)} positions for invalid links...")
    
    fixed_count = 0
    total_links_removed = 0
    
    # === CLEAN EACH POSITION ===
    for fen, video_links_json in rows:
        try:
            video_links = json.loads(video_links_json)
        except json.JSONDecodeError:
            print(f"[WARNING] Could not parse JSON for FEN: {fen[:50]}...")
            continue
        
        # Keep only links that are NOT Chess.com game URLs
        cleaned_links = [
            link for link in video_links 
            if not CHESS_URL_PATTERN.search(link)
        ]
        
        links_removed = len(video_links) - len(cleaned_links)
        
        # Only update database if something changed
        if links_removed > 0:
            cur.execute(
                "UPDATE positions SET video_links = ? WHERE fen = ?",
                (json.dumps(cleaned_links), fen)
            )
            fixed_count += 1
            total_links_removed += links_removed
            
            if fixed_count <= 5:  # Show details for first 5 positions
                print(f"  ✓ Cleaned FEN: {fen[:50]}...")
                print(f"    Removed {links_removed} Chess.com link(s)")
    
    # === SAVE CHANGES ===
    conn.commit()
    conn.close()
    
    # === SUMMARY ===
    print(f"\n{'='*60}")
    print(f"[OK] Database cleaning complete!")
    print(f"[INFO] Positions cleaned: {fixed_count}")
    print(f"[INFO] Total links removed: {total_links_removed}")
    print(f"{'='*60}")
    
    if fixed_count == 0:
        print("[INFO] Database was already clean - no changes needed.")


if __name__ == "__main__":
    main()

