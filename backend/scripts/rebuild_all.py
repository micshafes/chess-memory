"""
Master rebuild script: Rebuild everything from scratch with all game data.

This script will:
1. Delete and rebuild the SQLite database from ALL game data files
2. Fetch YouTube titles for all videos
3. Export to frontend JSON with titles

Run this anytime you add new games or want to rebuild from scratch.
"""

import subprocess
import sys
import os
import sqlite3

def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        print(f"[OK] {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error running {script_name}: {e}")
        return False
    except FileNotFoundError:
        print(f"[ERROR] Script not found: {script_path}")
        return False

def delete_database():
    """Delete the existing database to start fresh."""
    db_path = os.path.abspath("../../data/sqlite/chess_positions.db")
    
    if os.path.exists(db_path):
        print(f"\n[INFO] Deleting existing database: {db_path}")
        os.remove(db_path)
        print(f"[OK] Database deleted")
    else:
        print(f"\n[INFO] No existing database found, starting fresh")

def main():
    print("\n" + "="*60)
    print("  COMPLETE DATABASE REBUILD")
    print("  Processing ALL game series")
    print("="*60)
    
    # Step 0: Delete existing database
    delete_database()
    
    # Step 1: Rebuild SQLite from all game JSONs
    if not run_script("build_sqlite.py", "Step 1: Building SQLite from ALL game data"):
        print("\n[!] Failed to build database. Aborting.")
        return
    
    # Step 2: Fetch YouTube titles
    if not run_script("fetch_youtube_titles.py", "Step 2: Fetching YouTube titles"):
        print("\n[!] Failed to fetch titles. Aborting.")
        return
    
    # Step 3: Export to frontend JSON
    if not run_script("build_json_from_sqlite.py", "Step 3: Exporting to frontend JSON"):
        print("\n[!] Failed to export JSON. Aborting.")
        return
    
    print("\n" + "="*60)
    print("  ALL DONE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Copy data/json/chess_positions_frontend.json to frontend/chess_positions.json")
    print("  2. Refresh your browser (Ctrl+Shift+R)")
    print("  3. You should now see ALL games with real YouTube titles!\n")

if __name__ == "__main__":
    main()

