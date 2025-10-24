import sqlite3
import json
import os

# === CONFIG ===
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")
OUTPUT_FILE = os.path.abspath("../../data/json/chess_positions_frontend.json")

# Ensure output folder exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# === CONNECT TO DB ===
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# === QUERY ALL POSITIONS ===
cur.execute("SELECT fen, video_links, next_moves_by_daniel, next_moves_faced, video_metadata FROM positions")
rows = cur.fetchall()

print(f"Found {len(rows)} positions in the database. Exporting to JSON...")

# === BUILD JSON STRUCTURE ===
positions = []

for fen, video_links_json, next_by_daniel_json, next_faced_json, video_metadata_json in rows:
    # Use video_metadata if available, otherwise fall back to video_links
    video_metadata = json.loads(video_metadata_json) if video_metadata_json else []
    
    # If no metadata, create basic metadata from URLs
    if not video_metadata:
        video_urls = json.loads(video_links_json)
        video_metadata = [{"url": url, "title": None} for url in video_urls]
    
    position_entry = {
        "fen": fen,
        "videos": video_metadata,  # Now contains {url, title, video_id}
        "next_by_daniel": json.loads(next_by_daniel_json),
        "next_faced": json.loads(next_faced_json)
    }
    positions.append(position_entry)

# === WRITE TO FILE ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(positions, f, indent=2, ensure_ascii=False)

print(f"[OK] Export complete! JSON file written to {OUTPUT_FILE} with {len(positions)} positions.")

conn.close()
