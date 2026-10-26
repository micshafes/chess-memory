#!/usr/bin/env python3
"""
STEP 5: Export Database to Frontend JSON
=========================================

This script exports the SQLite database to a JSON file optimized for the frontend.

Purpose:
--------
The frontend is a static web application that needs all data in a single JSON file.
This script converts the SQLite database into the exact format the frontend expects.

The output JSON is loaded once when the page loads, then all lookups happen in memory
for instant response times.

Input:
------
- SQLite database: data/sqlite/chess_positions.db
- Optional: data/json/video_view_counts.json (from fetch_view_counts.py)

Output:
-------
- JSON file: data/json/chess_positions_frontend.json
  
Format:
  [
    {
      "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
      "videos": [
        {
          "url": "https://youtu.be/VIDEO_ID?t=123",
          "video_id": "VIDEO_ID",
          "title": "Speedrun to 1500 - Part 1",
          "danya_color": "white",   # or "black"; null if unknown
          "view_count": 123456      # null if view counts were not fetched
        }
      ],
      "next_by_daniel": ["e4", "d4", "Nf3"],
      "next_faced": ["e5", "c5", "d5"]
    },
    ...
  ]

File Size:
----------
The output JSON can be quite large (50-100MB) because it contains thousands of positions.
This is acceptable because:
- Modern browsers handle it well
- It's loaded once and cached
- gzip compression (automatic on most servers) reduces transfer size by ~80%

Usage:
------
    python 5_export_to_frontend_json.py
    
After running, copy the output file to frontend/chess_positions.json:
    cp data/json/chess_positions_frontend.json frontend/chess_positions.json
"""

import sqlite3
import json
import os

# === CONFIGURATION ===
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")
OUTPUT_FILE = os.path.abspath("../../data/json/chess_positions_frontend.json")
VIEW_COUNTS_FILE = os.path.abspath("../../data/json/video_view_counts.json")

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)


def main():
    """
    Main function to export database to JSON.
    
    Process:
    1. Connect to database
    2. Query all positions with their data
    3. Convert to frontend format
    4. Write to JSON file with pretty formatting
    """
    print("="*60)
    print("EXPORTING DATABASE TO FRONTEND JSON")
    print("="*60)
    
    # === CONNECT TO DATABASE ===
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # === LOAD VIEW COUNTS (optional) ===
    view_counts = {}
    if os.path.exists(VIEW_COUNTS_FILE):
        with open(VIEW_COUNTS_FILE, encoding="utf-8") as f:
            view_count_data = json.load(f)
        view_counts = view_count_data.get("view_counts", {})
        print(f"[INFO] Loaded {len(view_counts)} view counts "
              f"(fetched {view_count_data.get('fetched_at', 'unknown')})")
    else:
        print("[INFO] No view counts file; run fetch_view_counts.py to add them")

    # === QUERY ALL POSITIONS ===
    # Fetch all columns including the enriched video_metadata.
    # video_colors is missing in databases built before it was added.
    columns = [col[1] for col in cur.execute("PRAGMA table_info(positions)")]
    colors_column = "video_colors" if "video_colors" in columns else "NULL"
    cur.execute(f"""
        SELECT fen, video_links, next_moves_by_daniel, next_moves_faced, video_metadata,
               {colors_column}
        FROM positions
    """)
    rows = cur.fetchall()
    
    print(f"\n[INFO] Found {len(rows)} positions in database")
    print("[INFO] Converting to frontend format...\n")
    
    # === BUILD JSON STRUCTURE ===
    positions = []
    positions_with_metadata = 0
    positions_without_metadata = 0
    
    for (fen, video_links_json, next_by_daniel_json, next_faced_json,
         video_metadata_json, video_colors_json) in rows:
        # Prefer video_metadata (with titles) if available, otherwise fall back to video_links
        if video_metadata_json:
            video_metadata = json.loads(video_metadata_json)
            positions_with_metadata += 1
        else:
            # Fallback: create basic metadata from URLs without titles
            video_urls = json.loads(video_links_json) if video_links_json else []
            video_metadata = [{"url": url, "title": None, "video_id": None} for url in video_urls]
            positions_without_metadata += 1

        # Add Danya's color for each game link and the video's view count
        video_colors = json.loads(video_colors_json) if video_colors_json else {}
        for video in video_metadata:
            video["danya_color"] = video_colors.get(video["url"])
            video["view_count"] = view_counts.get(video["video_id"])

        # Build position entry in frontend format
        position_entry = {
            "fen": fen,
            "videos": video_metadata,  # {url, title, video_id, danya_color, view_count}
            "next_by_daniel": json.loads(next_by_daniel_json) if next_by_daniel_json else [],
            "next_faced": json.loads(next_faced_json) if next_faced_json else []
        }
        positions.append(position_entry)
    
    # === WRITE TO FILE ===
    print(f"[INFO] Writing JSON to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(positions, f, indent=2, ensure_ascii=False)
    
    # Get file size for reporting
    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    
    # === SUMMARY ===
    print(f"\n{'='*60}")
    print(f"[OK] Export complete!")
    print(f"{'='*60}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Total positions: {len(positions):,}")
    print(f"  - With YouTube titles: {positions_with_metadata:,}")
    print(f"  - Without titles: {positions_without_metadata:,}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"{'='*60}")
    print(f"\nNext step:")
    print(f"  Copy to frontend: cp {OUTPUT_FILE} frontend/chess_positions.json")
    print()
    
    conn.close()


if __name__ == "__main__":
    main()

