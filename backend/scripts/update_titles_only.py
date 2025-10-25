#!/usr/bin/env python3
"""
UTILITY: Update YouTube Titles Only
====================================

This script updates YouTube titles without rebuilding the entire database.

Purpose:
--------
If you only need to refresh video titles (e.g., because video titles changed on YouTube,
or you initially skipped fetching titles), this script runs just the title-fetching
and JSON export steps.

This is much faster than a full rebuild since it skips the time-consuming game processing.

Use Cases:
----------
- You added new game data and already rebuilt the database, just need titles
- YouTube video titles were updated and you want to refresh them
- You initially ran the pipeline without fetching titles

Steps:
------
1. Fetch YouTube titles (3_fetch_youtube_titles.py)
2. Export to frontend JSON (5_export_to_frontend_json.py)

Usage:
------
    python update_titles_only.py
    
Expected Runtime:
-----------------
- Step 1 (Fetch titles): 5-15 minutes
- Step 2 (Export JSON): < 1 minute
"""

import subprocess
import sys
import os

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
        result = subprocess.run([sys.executable, script_path], check=True)
        print(f"\n[OK] {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error running {script_name}: {e}")
        return False
    except FileNotFoundError:
        print(f"\n[ERROR] Script not found: {script_path}")
        return False

def main():
    """
    Main function to update titles and rebuild JSON.
    """
    print("\n" + "="*60)
    print("  YOUTUBE TITLE UPDATER")
    print("="*60)
    print("\nThis will fetch real YouTube titles and update your frontend.")
    print("The database must already exist - run rebuild_all.py first if needed.\n")
    
    # Step 1: Fetch YouTube titles
    if not run_script("3_fetch_youtube_titles.py", 
                     "Step 1: Fetching YouTube video titles"):
        print("\n[!] Failed to fetch titles. Aborting.")
        return
    
    # Step 2: Rebuild frontend JSON with new titles
    if not run_script("5_export_to_frontend_json.py", 
                     "Step 2: Rebuilding frontend JSON"):
        print("\n[!] Failed to rebuild JSON. Aborting.")
        return
    
    # === SUCCESS ===
    print("\n" + "="*60)
    print("  ✓ ALL DONE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Copy the generated JSON file to frontend:")
    print("     cp data/json/chess_positions_frontend.json frontend/chess_positions.json")
    print("")
    print("  2. Refresh your browser (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)")
    print("")
    print("  3. You should now see real YouTube video titles!")
    print("")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

