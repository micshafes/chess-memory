"""
Master script to fetch YouTube titles and rebuild the frontend JSON file.
Run this script to update your chess positions with real YouTube video titles.
"""

import subprocess
import sys
import os

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

def main():
    print("\n>>> YouTube Title Updater")
    print("This will fetch real YouTube titles and update your frontend.\n")
    
    # Step 1: Fetch YouTube titles
    if not run_script("fetch_youtube_titles.py", "Step 1: Fetching YouTube titles"):
        print("\n[!] Failed to fetch titles. Aborting.")
        return
    
    # Step 2: Rebuild JSON
    if not run_script("build_json_from_sqlite.py", "Step 2: Rebuilding frontend JSON"):
        print("\n[!] Failed to rebuild JSON. Aborting.")
        return
    
    print("\n" + "="*60)
    print("  ALL DONE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Copy the generated JSON file to frontend/chess_positions.json")
    print("  2. Refresh your browser (hard refresh with Ctrl+Shift+R)")
    print("  3. You should now see real YouTube video titles!\n")

if __name__ == "__main__":
    main()

