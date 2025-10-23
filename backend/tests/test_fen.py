import sqlite3
import json
import os

# Path to your DB
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

test_e4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3"
test_accelerated_dragon = "r1bqk1nr/pp1pppbp/2n3p1/8/3NP3/4B3/PPP2PPP/RN1QKB1R w KQkq -"
test_weird_accelerated_dragon = "r1bqk2r/pp1pppbp/2n2np1/8/3NP3/2P1BP2/PP4PP/RN1QKB1R b KQkq -"
test_h4 = "rnbqkbnr/pppppppp/8/8/7P/8/PPPPPPP1/RNBQKBNR b KQkq h3"
test_b3 = "rnbqkbnr/pppppppp/8/8/8/1P6/P1PPPPPP/RNBQKBNR b KQkq -"

# The FEN you want to test
fen_to_test = test_b3

# Query the DB
cur.execute("""
SELECT video_links, next_moves_by_daniel, next_moves_faced
FROM positions
WHERE fen = ?
""", (fen_to_test,))

row = cur.fetchone()
conn.close()
print("Testing FEN: ", fen_to_test)

if row:
    video_links = json.loads(row[0])
    next_by_daniel = json.loads(row[1])
    next_faced = json.loads(row[2])
    
    print("✅ FEN found!")
    print("Video links:", video_links)
    print("Next moves by Daniel:", next_by_daniel)
    print("Next moves Daniel faced:", next_faced)
else:
    print("❌ FEN not found in DB")
