import sqlite3
import json
import os

DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Create table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS positions (
    fen TEXT PRIMARY KEY,
    video_links TEXT,
    next_moves_by_daniel TEXT,
    next_moves_faced TEXT
)
""")

# Insert a dummy FEN
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
videos = ["https://youtu.be/test?t=0"]
next_by_daniel = ["e4", "d4"]
next_faced = ["e5", "c5"]

cur.execute("""
INSERT OR REPLACE INTO positions (fen, video_links, next_moves_by_daniel, next_moves_faced)
VALUES (?, ?, ?, ?)
""", (fen, json.dumps(videos), json.dumps(next_by_daniel), json.dumps(next_faced)))

conn.commit()

# Read it back
cur.execute("SELECT * FROM positions WHERE fen = ?", (fen,))
row = cur.fetchone()
conn.close()

if row:
    print("✅ Success! Read from DB:")
    print("FEN:", row[0])
    print("Videos:", json.loads(row[1]))
    print("Next moves by Daniel:", json.loads(row[2]))
    print("Next moves faced:", json.loads(row[3]))
else:
    print("❌ Could not read from DB")
