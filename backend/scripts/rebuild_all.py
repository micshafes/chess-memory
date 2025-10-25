#!/usr/bin/env python3
"""
MASTER SCRIPT: Complete Database Rebuild
=========================================

This script orchestrates a complete rebuild of the entire chess positions database.

Purpose:
--------
Run this script whenever you:
- Add new game data JSON files
- Want to rebuild from scratch
- Need to ensure all data is fresh and synchronized

The script runs all 5 pipeline steps in order:
1. Build SQLite database from ALL game data files
2. Fetch YouTube video titles for all positions
3. Clean any invalid links from the database
4. Export final data to frontend JSON

Input:
------
- Game data JSON files in data/json/ (e.g., back_to_3000_game_data.json, etc.)

Output:
-------
- Fresh SQLite database: data/sqlite/chess_positions.db
- Frontend JSON file: data/json/chess_positions_frontend.json

Safety:
-------
The script deletes the existing database before rebuilding. This ensures a clean slate
but means you should back up any custom modifications first.

Usage:
------
    python rebuild_all.py
    
Expected Runtime:
-----------------
- Step 1 (Build DB): 2-5 minutes
- Step 2 (Fetch titles): 5-15 minutes (depends on number of unique videos)
- Step 3 (Clean DB): < 1 minute
- Step 4 (Export JSON): < 1 minute

Total: ~10-20 minutes for a full rebuild
"""

import subprocess
import sys
import os
import sqlite3

def run_script(script_name, description):
    """
    Run a Python script and handle errors gracefully.
    
    Args:
        script_name: Name of the script file to run
        description: Human-readable description for logging
        
    Returns:
        True if script ran successfully, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    try:
        # Run the script as a subprocess
        result = subprocess.run([sys.executable, script_path], check=True)
        print(f"\n[OK] {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error running {script_name}: {e}")
        print("[ERROR] Aborting rebuild process.")
        return False
    except FileNotFoundError:
        print(f"\n[ERROR] Script not found: {script_path}")
        print("[ERROR] Make sure all numbered scripts are in the same directory.")
        return False

def delete_database():
    """
    Delete the existing database to ensure a completely fresh start.
    
    This prevents any issues with:
    - Stale data
    - Schema changes
    - Corrupted entries
    """
    db_path = os.path.abspath("../../data/sqlite/chess_positions.db")
    
    if os.path.exists(db_path):
        print(f"\n[INFO] Deleting existing database: {db_path}")
        try:
            os.remove(db_path)
            print(f"[OK] Database deleted successfully")
        except Exception as e:
            print(f"[ERROR] Could not delete database: {e}")
            print("[ERROR] Please delete it manually and try again.")
            return False
    else:
        print(f"\n[INFO] No existing database found - starting fresh")
    
    return True

def main():
    """
    Main rebuild orchestration function.
    
    Runs all pipeline steps in sequence:
    1. Delete old database
    2. Build new database from game data
    3. Fetch YouTube titles
    4. Clean invalid links
    5. Export to frontend JSON
    """
    print("\n" + "="*60)
    print("  COMPLETE DATABASE REBUILD")
    print("  Processing ALL game series")
    print("="*60)
    print("\nThis will:")
    print("  1. Delete existing database")
    print("  2. Build fresh database from all game data")
    print("  3. Fetch YouTube titles (may take 10+ minutes)")
    print("  4. Clean any invalid links")
    print("  5. Export to frontend JSON")
    print("\n" + "="*60)
    
    # Step 0: Delete existing database for clean rebuild
    if not delete_database():
        return
    
    # Step 1: Build SQLite database from all game JSON files
    if not run_script("2_build_database_from_games.py", 
                     "Step 1: Building SQLite database from ALL game data"):
        return
    
    # Step 2: Fetch YouTube titles for all videos
    if not run_script("3_fetch_youtube_titles.py", 
                     "Step 2: Fetching YouTube video titles"):
        return
    
    # Step 3: Clean any Chess.com URLs from video_links
    if not run_script("4_clean_database.py", 
                     "Step 3: Cleaning database of invalid links"):
        return
    
    # Step 4: Export to frontend JSON format
    if not run_script("5_export_to_frontend_json.py", 
                     "Step 4: Exporting to frontend JSON"):
        return
    
    # === SUCCESS ===
    print("\n" + "="*60)
    print("  ✓ ALL DONE! Database rebuild complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Copy the JSON file to frontend:")
    print("     cp data/json/chess_positions_frontend.json frontend/chess_positions.json")
    print("")
    print("  2. Refresh your browser (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)")
    print("")
    print("  3. You should now see ALL games with real YouTube titles!")
    print("")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
