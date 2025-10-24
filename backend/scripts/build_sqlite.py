import json
import sqlite3
import chess
import chess.pgn
from io import StringIO
from urllib.parse import urlparse, parse_qs
import re
import os

# === CONFIG ===
INPUT_FILE = os.path.abspath("../../data/json/top_theory_game_data.json")
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")

# Ensure the folder exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# === DATABASE SETUP ===
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS positions (
    fen TEXT PRIMARY KEY,
    video_links TEXT,
    next_moves_by_daniel TEXT,
    next_moves_faced TEXT
)
""")
conn.commit()

# === HELPERS ===
def parse_clock(comment):
    """Extract clock time in seconds from a PGN comment like {[%clk 0:03:01.9]}"""
    match = re.search(r"\[%clk\s+(\d+):(\d+):([\d.]+)\]", comment)
    if not match:
        return None
    minutes = int(match.group(1))
    seconds = int(match.group(2))
    tenths = float(match.group(3))
    return minutes * 60 + seconds + tenths

def get_youtube_start_time(url):
    """Extract base timestamp (t= param) from YouTube URL."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    try:
        return int(qs.get("t", [0])[0])
    except ValueError:
        return 0

# === LOAD JSON ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    games = json.load(f)

print(f"Found {len(games)} games. Starting processing...")

# === PROCESS EACH GAME ===
for idx, entry in enumerate(games, 1):
    api_game = entry["api_game"]
    csv_game = entry["csv_game"]

    youtube_url = csv_game["youtube_url"]
    youtube_start = get_youtube_start_time(youtube_url)
    pgn_text = api_game["pgn"]

    game = chess.pgn.read_game(StringIO(pgn_text))
    if game is None:
        print(f"⚠️ Could not parse game: {api_game.get('url', 'unknown')}")
        continue

    daniel_color = "white" if api_game["white"]["username"].lower() == "senseidanya" else "black"
    board = game.board()
    positions = {}

    last_clock_white = None
    last_clock_black = None
    total_time_elapsed = 0.0

    # Use mainline() to iterate all moves
    for move_node in game.mainline():
        fen_before = board.fen()
        move = move_node.move
        comment = move_node.comment
        to_move = "white" if board.turn == chess.WHITE else "black"

        # Parse clock
        current_clock = parse_clock(comment)
        if to_move == "white" and last_clock_white is not None and current_clock is not None:
            elapsed = last_clock_white - current_clock
            if elapsed > 0:
                total_time_elapsed += elapsed
        elif to_move == "black" and last_clock_black is not None and current_clock is not None:
            elapsed = last_clock_black - current_clock
            if elapsed > 0:
                total_time_elapsed += elapsed

        if to_move == "white":
            last_clock_white = current_clock
        else:
            last_clock_black = current_clock

        # Normalize FEN
        # Combine board layout, side to move, castling rights, en passant square
        fen_no_counts = board.board_fen() + ' ' + \
                ('w' if board.turn == chess.WHITE else 'b') + ' ' + \
                board.castling_xfen() + ' ' + \
                (chess.square_name(board.ep_square) if board.ep_square is not None else '-')
        fen_before = fen_no_counts

        # Initialize FEN entry
        if fen_before not in positions:
            positions[fen_before] = {"videos": [], "next_by_daniel": set(), "next_faced": set()}

        # Build YouTube link
        link_time = youtube_start + int(total_time_elapsed)
        video_link = youtube_url.split("&t=")[0] + f"&t={link_time}"
        positions[fen_before]["videos"].append(video_link)

        # Track next moves
        daniel_to_move = (to_move == daniel_color)
        san_move = board.san(move)
        if daniel_to_move:
            positions[fen_before]["next_by_daniel"].add(san_move)
        else:
            positions[fen_before]["next_faced"].add(san_move)

        board.push(move)

    # Insert positions into SQLite
    for fen, info in positions.items():
        # 1️⃣ Check if FEN exists
        cur.execute("SELECT video_links, next_moves_by_daniel, next_moves_faced FROM positions WHERE fen = ?", (fen,))
        row = cur.fetchone()

        if row:
            # Merge existing lists with new ones
            existing_videos = set(json.loads(row[0]))
            existing_next_by_daniel = set(json.loads(row[1]))
            existing_next_faced = set(json.loads(row[2]))

            new_videos = existing_videos.union(info["videos"])
            new_next_by_daniel = existing_next_by_daniel.union(info["next_by_daniel"])
            new_next_faced = existing_next_faced.union(info["next_faced"])

            cur.execute("""
                UPDATE positions
                SET video_links = ?, next_moves_by_daniel = ?, next_moves_faced = ?
                WHERE fen = ?
            """, (
                json.dumps(list(new_videos)),
                json.dumps(list(new_next_by_daniel)),
                json.dumps(list(new_next_faced)),
                fen
            ))
        else:
            cur.execute("""
                INSERT INTO positions (fen, video_links, next_moves_by_daniel, next_moves_faced)
                VALUES (?, ?, ?, ?)
            """, (
                fen,
                json.dumps(list(info["videos"])),
                json.dumps(list(info["next_by_daniel"])),
                json.dumps(list(info["next_faced"]))
            ))

            if idx % 10 == 0 or idx == len(games):
                print(f"Processed {idx}/{len(games)} games...")

conn.commit()
conn.close()
print("✅ All positions stored in chess_positions.db with real clock times.")
