import sqlite3
import json
import re
import os

DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")

# Regex to detect Chess.com URLs
chess_url_pattern = re.compile(r"https?://(www\.)?chess\.com/game/live/\d+")

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Fetch all positions
cur.execute("SELECT fen, video_links FROM positions")
rows = cur.fetchall()
fixed_count = 0

for fen, video_links_json in rows:
    try:
        video_links = json.loads(video_links_json)
    except json.JSONDecodeError:
        continue

    # Keep only links that are not chess.com game URLs
    cleaned_links = [link for link in video_links if not chess_url_pattern.search(link)]

    if len(cleaned_links) != len(video_links):
        # Update DB only if something changed
        cur.execute(
            "UPDATE positions SET video_links = ? WHERE fen = ?",
            (json.dumps(cleaned_links), fen)
        )
        fixed_count += 1

conn.commit()
conn.close()
print(f"✅ Cleaned {fixed_count} positions that had chess.com links in video_links.")
