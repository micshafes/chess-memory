# Backend Scripts - Data Pipeline

This directory contains the scripts for processing Daniel Naroditsky's chess speedrun games and building the position database.

## Overview

The data pipeline converts CSV files (with YouTube + Chess.com URLs) into a searchable database of chess positions that powers the frontend application.

```
CSV Files → Match with API → Extract Positions → Fetch Titles → Export JSON → Frontend
```

## Data Pipeline Scripts

Run these scripts in order (or use `rebuild_all.py`):

### 1. Match Games with API (`1_match_games_csv_to_api.py`)

**Purpose**: Matches CSV game references with full game data from Chess.com API.

**Input**:
- CSV files in `data/csv/` with columns:
  - Column 0: YouTube URL with timestamp
  - Column 1: Chess.com game URL

**Output**:
- `game_matches.json` - Matched game data with PGN

**Usage**:
```bash
python 1_match_games_csv_to_api.py
```

**Notes**:
- Modify the `CSV_FILE` path in `main()` to process different speedrun series
- Uses Chess.com's public API (no authentication required)
- Includes retry logic and rate limiting

---

### 2. Build Database (`2_build_database_from_games.py`)

**Purpose**: Extracts all chess positions from games and builds SQLite database.

**Input**:
- Game data JSON files in `data/json/`:
  - `back_to_3000_game_data.json`
  - `beginner_to_master_game_data.json`
  - `develop_your_instincts_game_data.json`
  - `master_class_game_data.json`
  - `sensei_speedrun_game_data.json`
  - `top_theory_game_data.json`

**Output**:
- `data/sqlite/chess_positions.db` with positions table

**What it tracks**:
- Every unique position (FEN notation)
- Moves Danya played from each position
- Moves opponents played from each position
- YouTube video links with precise timestamps

**Usage**:
```bash
python 2_build_database_from_games.py
```

**Technical details**:
- Parses PGN to extract positions
- Calculates video timestamps using move clock times
- Normalizes FEN (removes move counters for better matching)
- Merges data if position already exists

---

### 3. Fetch YouTube Titles (`3_fetch_youtube_titles.py`)

**Purpose**: Enriches database with actual YouTube video titles.

**API Used**: YouTube oEmbed API (no API key required)

**Output**:
- Updates database with `video_metadata` column containing:
  ```json
  {
    "url": "https://youtu.be/VIDEO_ID?t=123",
    "video_id": "VIDEO_ID",
    "title": "Speedrun to 1500 - Part 1"
  }
  ```

**Usage**:
```bash
python 3_fetch_youtube_titles.py
```

**Performance**:
- Caches titles to avoid duplicate API calls
- Adds 0.1s delay between requests
- Commits every 100 positions
- Typical runtime: 5-15 minutes

---

### 4. Clean Database (`4_clean_database.py`)

**Purpose**: Removes any Chess.com URLs that were accidentally added to video_links.

**Usage**:
```bash
python 4_clean_database.py
```

**Notes**:
- Safety/maintenance script
- Only modifies positions with invalid links
- Prints summary of changes

---

### 5. Export to Frontend JSON (`5_export_to_frontend_json.py`)

**Purpose**: Converts SQLite database to JSON format for frontend.

**Output**:
- `data/json/chess_positions_frontend.json` (50-100MB)

**Format**:
```json
[
  {
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
    "videos": [
      {
        "url": "https://youtu.be/VIDEO_ID?t=123",
        "video_id": "VIDEO_ID",
        "title": "Speedrun to 1500 - Part 1"
      }
    ],
    "next_by_daniel": ["e4", "d4", "Nf3"],
    "next_faced": ["e5", "c5", "d5"]
  }
]
```

**Usage**:
```bash
python 5_export_to_frontend_json.py
```

**After running**:
```bash
cp data/json/chess_positions_frontend.json frontend/chess_positions.json
```

---

## Utility Scripts

### Complete Rebuild (`rebuild_all.py`)

Runs the entire pipeline from scratch:
1. Deletes existing database
2. Builds fresh database from all game data
3. Fetches YouTube titles
4. Cleans invalid links
5. Exports to frontend JSON

**Usage**:
```bash
python rebuild_all.py
```

**When to use**:
- Adding new game data files
- Fresh start after data issues
- Ensuring complete synchronization

**Runtime**: ~10-20 minutes

---

### Update Titles Only (`update_titles_only.py`)

Refreshes YouTube titles without rebuilding database.

**Usage**:
```bash
python update_titles_only.py
```

**When to use**:
- YouTube video titles changed
- You initially skipped fetching titles
- Quick refresh needed

**Runtime**: ~5-15 minutes

---

### Development Test Tool (`dev_test_chess_api.py`)

Tests Chess.com API connectivity and game data extraction.

**Usage**:
```bash
python dev_test_chess_api.py
```

**Use cases**:
- Debugging API issues
- Testing new game URLs
- Verifying PGN parsing
- Development and troubleshooting

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP requests for APIs
- `python-chess` - Chess game processing and PGN parsing

---

## File Structure

```
backend/scripts/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
│
├── 1_match_games_csv_to_api.py        # Step 1: Match CSV with API
├── 2_build_database_from_games.py     # Step 2: Build database
├── 3_fetch_youtube_titles.py          # Step 3: Fetch titles
├── 4_clean_database.py                # Step 4: Clean database
├── 5_export_to_frontend_json.py       # Step 5: Export JSON
│
├── rebuild_all.py                      # Utility: Complete rebuild
├── update_titles_only.py               # Utility: Update titles
└── dev_test_chess_api.py               # Dev tool: Test API
```

---

## Common Issues

### Chess.com API Returns 403 Forbidden
- **Cause**: Rate limiting or IP blocking
- **Solution**: Script includes delays and proper headers; wait and retry

### YouTube Title Fetch Fails
- **Cause**: Video is private/deleted or API rate limit
- **Solution**: Script handles gracefully with fallback titles

### Large JSON File Size
- **Cause**: Many positions (50-100MB is normal)
- **Solution**: Web servers auto-compress with gzip (~80% reduction)

### Script Crashes Mid-Run
- **Cause**: Network issues or system interruption
- **Solution**: Most scripts commit progress regularly; safe to restart

---

## Data Flow Diagram

```
CSV Files (YouTube + Chess.com URLs)
         ↓
[1_match_games_csv_to_api.py]
         ↓
Game Data JSON (with PGN)
         ↓
[2_build_database_from_games.py]
         ↓
SQLite Database (positions)
         ↓
[3_fetch_youtube_titles.py]
         ↓
SQLite Database (+ video metadata)
         ↓
[4_clean_database.py]
         ↓
SQLite Database (cleaned)
         ↓
[5_export_to_frontend_json.py]
         ↓
Frontend JSON
         ↓
Copy to frontend/chess_positions.json
         ↓
User's Browser (loads once, caches)
```

---

## Quick Start

To rebuild everything from scratch:

```bash
# Navigate to scripts directory
cd backend/scripts

# Run complete rebuild
python rebuild_all.py

# Copy output to frontend
cp ../../data/json/chess_positions_frontend.json ../../frontend/chess_positions.json
```

Then refresh your browser!

---

## Contributing

When adding new features:
1. Follow the existing naming convention
2. Add comprehensive docstrings
3. Include error handling
4. Test with a small dataset first
5. Update this README

---

## Database Schema

### Positions Table

| Column | Type | Description |
|--------|------|-------------|
| `fen` | TEXT (PRIMARY KEY) | Chess position in FEN notation (first 4 components) |
| `video_links` | TEXT (JSON array) | Legacy: YouTube URLs with timestamps |
| `next_moves_by_daniel` | TEXT (JSON array) | Moves Danya played from this position |
| `next_moves_faced` | TEXT (JSON array) | Moves opponents played from this position |
| `video_metadata` | TEXT (JSON array) | Enriched: URLs + titles + video IDs |

### Example Position Entry

```sql
fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3"
video_links: ["https://youtu.be/ABC?t=123", "https://youtu.be/XYZ?t=456"]
next_moves_by_daniel: ["Nf3", "Nc3", "d4"]
next_moves_faced: ["e5", "c5", "d6"]
video_metadata: [
  {
    "url": "https://youtu.be/ABC?t=123",
    "video_id": "ABC",
    "title": "Speedrun to 1200 - Part 3: Central Control"
  }
]
```

---

## License

This project is for educational purposes. Chess game data is from public Chess.com games, and YouTube content belongs to Daniel Naroditsky.

