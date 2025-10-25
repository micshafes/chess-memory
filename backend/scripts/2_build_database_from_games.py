#!/usr/bin/env python3
"""
STEP 2: Build SQLite Database from Game Data
=============================================

This script processes matched game data and builds a SQLite database of chess positions.

Purpose:
--------
Takes game data (PGN format) and extracts every chess position that occurred in Danya's games.
For each position, tracks:
- The FEN (position notation)
- Which moves Danya played from that position
- Which moves opponents played from that position  
- YouTube video links with timestamps to that position

The resulting database allows the frontend to look up any position and see:
1. What Danya typically plays in that position
2. What opponents have tried against Danya
3. Video links to watch Danya handle that position

Input:
------
- Game data JSON files in data/json/:
  - back_to_3000_game_data.json
  - beginner_to_master_game_data.json
  - develop_your_instincts_game_data.json
  - master_class_game_data.json
  - sensei_speedrun_game_data.json
  - top_theory_game_data.json

Output:
-------
- SQLite database (data/sqlite/chess_positions.db) with table:
  positions (
    fen TEXT PRIMARY KEY,           -- Chess position in FEN notation
    video_links TEXT,                -- JSON array of YouTube URLs
    next_moves_by_daniel TEXT,       -- JSON array of moves Danya played
    next_moves_faced TEXT            -- JSON array of moves opponents played
  )

Usage:
------
    python 2_build_database_from_games.py
"""

import json
import sqlite3
import chess
import chess.pgn
from io import StringIO
from urllib.parse import urlparse, parse_qs
import re
import os

# === CONFIGURATION ===
# List of all game data JSON files to process
INPUT_FILES = [
    "back_to_3000_game_data.json",
    "beginner_to_master_game_data.json",
    "develop_your_instincts_game_data.json",
    "master_class_game_data.json",
    "sensei_speedrun_game_data.json",
    "top_theory_game_data.json"
]

# Output database path
DB_FILE = os.path.abspath("../../data/sqlite/chess_positions.db")

# Ensure the output folder exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# === DATABASE SETUP ===
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Create positions table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS positions (
    fen TEXT PRIMARY KEY,
    video_links TEXT,
    next_moves_by_daniel TEXT,
    next_moves_faced TEXT
)
""")
conn.commit()


# === HELPER FUNCTIONS ===

def parse_clock(comment):
    """
    Extract clock time in seconds from a PGN comment.
    
    Chess.com PGN files include clock times in comments like: {[%clk 0:03:01.9]}
    This extracts the time and converts it to total seconds.
    
    Args:
        comment: PGN move comment string
        
    Returns:
        Total time in seconds, or None if no clock found
        
    Example:
        parse_clock("{[%clk 0:03:01.9]}") -> 181.9
    """
    match = re.search(r"\[%clk\s+(\d+):(\d+):([\d.]+)\]", comment)
    if not match:
        return None
    
    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    
    return hours * 3600 + minutes * 60 + seconds


def get_youtube_start_time(url):
    """
    Extract the base timestamp (t= parameter) from a YouTube URL.
    
    Args:
        url: YouTube URL (e.g., https://youtu.be/VIDEO_ID?t=123)
        
    Returns:
        Timestamp in seconds (int), or 0 if not found
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    try:
        return int(qs.get("t", [0])[0])
    except ValueError:
        return 0


def normalize_fen(fen_string):
    """
    Normalize a FEN string to only include position-critical components.
    
    Full FEN includes 6 components:
    1. Piece placement
    2. Active color (w/b)
    3. Castling rights
    4. En passant target
    5. Halfmove clock (not needed for position matching)
    6. Fullmove number (not needed for position matching)
    
    We only keep the first 4 components for position matching.
    
    Args:
        fen_string: Full FEN notation
        
    Returns:
        Normalized FEN with only first 4 components
    """
    parts = fen_string.split(' ')
    return ' '.join(parts[:4])


# === MAIN PROCESSING ===

total_games_processed = 0

# Process each game data file
for file_name in INPUT_FILES:
    INPUT_FILE = os.path.abspath(f"../../data/json/{file_name}")
    
    print(f"\n{'='*60}")
    print(f"Processing: {file_name}")
    print(f"{'='*60}")
    
    # === LOAD GAME DATA ===
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        games = json.load(f)
    
    print(f"Found {len(games)} games in {file_name}")
    
    # === PROCESS EACH GAME ===
    for idx, entry in enumerate(games, 1):
        api_game = entry["api_game"]
        csv_game = entry["csv_game"]

        youtube_url = csv_game["youtube_url"]
        youtube_start = get_youtube_start_time(youtube_url)
        pgn_text = api_game["pgn"]

        # Parse PGN
        game = chess.pgn.read_game(StringIO(pgn_text))
        if game is None:
            print(f"[!] Could not parse game: {api_game.get('url', 'unknown')}")
            continue

        # Determine which color Danya is playing
        # Danya's known Chess.com usernames
        daniel_usernames = {
            "senseidanya",
            "ohmylands",
            "frankfurtairport",
            "hebeccararis"
        }
        
        white_username = api_game["white"]["username"].lower()
        daniel_color = "white" if white_username in daniel_usernames else "black"
        
        # Initialize board and position tracker
        board = game.board()
        positions = {}  # FEN -> {videos, next_by_daniel, next_faced}

        # Clock tracking for calculating elapsed time
        last_clock_white = None
        last_clock_black = None
        total_time_elapsed = 0.0

        # Iterate through all moves in the game
        for move_node in game.mainline():
            move = move_node.move
            comment = move_node.comment
            to_move = "white" if board.turn == chess.WHITE else "black"

            # === Calculate elapsed time from clock ===
            current_clock = parse_clock(comment)
            
            # Track time elapsed for video timestamp calculation
            if to_move == "white" and last_clock_white is not None and current_clock is not None:
                elapsed = last_clock_white - current_clock
                if elapsed > 0:
                    total_time_elapsed += elapsed
            elif to_move == "black" and last_clock_black is not None and current_clock is not None:
                elapsed = last_clock_black - current_clock
                if elapsed > 0:
                    total_time_elapsed += elapsed

            # Update last known clocks
            if to_move == "white":
                last_clock_white = current_clock
            else:
                last_clock_black = current_clock

            # === Normalize FEN (remove move counters) ===
            # Combine: board layout + turn + castling + en passant
            fen_normalized = board.board_fen() + ' ' + \
                           ('w' if board.turn == chess.WHITE else 'b') + ' ' + \
                           board.castling_xfen() + ' ' + \
                           (chess.square_name(board.ep_square) if board.ep_square is not None else '-')

            # === Initialize position entry ===
            if fen_normalized not in positions:
                positions[fen_normalized] = {
                    "videos": [],
                    "next_by_daniel": set(),
                    "next_faced": set()
                }

            # === Build YouTube link with timestamp ===
            link_time = youtube_start + int(total_time_elapsed)
            video_link = youtube_url.split("&t=")[0] + f"&t={link_time}"
            positions[fen_normalized]["videos"].append(video_link)

            # === Track which moves were played ===
            daniel_to_move = (to_move == daniel_color)
            san_move = board.san(move)  # Standard Algebraic Notation (e.g., "Nf3")
            
            if daniel_to_move:
                positions[fen_normalized]["next_by_daniel"].add(san_move)
            else:
                positions[fen_normalized]["next_faced"].add(san_move)

            # Apply the move to the board
            board.push(move)

        # === INSERT/UPDATE DATABASE ===
        for fen, info in positions.items():
            # Check if this FEN already exists in database
            cur.execute(
                "SELECT video_links, next_moves_by_daniel, next_moves_faced FROM positions WHERE fen = ?",
                (fen,)
            )
            row = cur.fetchone()

            if row:
                # Merge with existing data
                existing_videos = set(json.loads(row[0]))
                existing_next_by_daniel = set(json.loads(row[1]))
                existing_next_faced = set(json.loads(row[2]))

                # Combine old and new data
                new_videos = existing_videos.union(info["videos"])
                new_next_by_daniel = existing_next_by_daniel.union(info["next_by_daniel"])
                new_next_faced = existing_next_faced.union(info["next_faced"])

                # Update database
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
                # Insert new position
                cur.execute("""
                    INSERT INTO positions (fen, video_links, next_moves_by_daniel, next_moves_faced)
                    VALUES (?, ?, ?, ?)
                """, (
                    fen,
                    json.dumps(list(info["videos"])),
                    json.dumps(list(info["next_by_daniel"])),
                    json.dumps(list(info["next_faced"]))
                ))

        # Progress update
        if idx % 10 == 0 or idx == len(games):
            print(f"  Processed {idx}/{len(games)} games...")
    
    total_games_processed += len(games)
    print(f"[OK] Completed {file_name}: {len(games)} games")
    
    # Commit after each file
    conn.commit()

# === CLEANUP ===
conn.close()

print(f"\n{'='*60}")
print(f"[OK] All positions stored in chess_positions.db")
print(f"[OK] Total games processed: {total_games_processed}")
print(f"{'='*60}")

