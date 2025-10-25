#!/usr/bin/env python3
"""
STEP 1: Match CSV Games with Chess.com API Data
================================================

This script matches chess games from CSV files with their corresponding data from the Chess.com API.

Purpose:
--------
Daniel Naroditsky's speedrun games are tracked in CSV files with YouTube URLs and Chess.com game URLs.
This script fetches the full game data (including PGN with move timings) from Chess.com's API
and creates a matched dataset ready for database import.

Input:
------
- CSV files in data/csv/ containing:
  - Column 0: YouTube URL with timestamp (e.g., https://youtu.be/VIDEO_ID?t=123)
  - Column 1: Chess.com game URL (e.g., https://www.chess.com/game/live/GAME_ID)

Output:
-------
- JSON file (game_matches.json) containing matched game data with:
  - CSV metadata (YouTube URL, timestamps)
  - API game data (PGN, player info, etc.)
  - Match status (FOUND/NOT_FOUND)

Usage:
------
    python 1_match_games_csv_to_api.py
    
Note: Modify the CSV_FILE path in main() to process different speedrun series.
"""

import requests
import json
import csv
import re
from datetime import datetime
from typing import List, Dict, Optional

class ChessGameMatcher:
    """
    Matches chess games from CSV files with Chess.com API data.
    
    Attributes:
        csv_file (str): Path to the CSV file containing game URLs
        csv_games (List[Dict]): Parsed games from CSV
        api_games (List[Dict]): Games fetched from API
        matches (List[Dict]): Matched CSV games with API data
    """
    
    def __init__(self, csv_file: str):
        """
        Initialize the matcher with a CSV file path.
        
        Args:
            csv_file: Path to CSV file with YouTube and Chess.com URLs
        """
        self.csv_file = csv_file
        self.csv_games = []
        self.api_games = []
        self.matches = []
        
    def load_csv_games(self) -> List[Dict]:
        """
        Load and parse chess games from CSV file.
        
        Returns:
            List of dictionaries containing game data from CSV:
                - row_number: CSV row number
                - youtube_url: YouTube video URL with timestamp
                - chess_url: Chess.com game URL
                - game_id: Extracted Chess.com game ID
                - youtube_timestamp: Extracted timestamp in seconds
        """
        print("Loading CSV games...")
        self.csv_games = []
        
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) >= 2:
                    youtube_url = row[0].strip()
                    chess_url = row[1].strip()
                    
                    # Extract game ID from Chess.com URL
                    game_id = self.extract_game_id_from_url(chess_url)
                    
                    if game_id:
                        game_data = {
                            'row_number': row_num,
                            'youtube_url': youtube_url,
                            'chess_url': chess_url,
                            'game_id': game_id,
                            'youtube_timestamp': self.extract_youtube_timestamp(youtube_url)
                        }
                        self.csv_games.append(game_data)
                        print(f"  Row {row_num}: Game ID {game_id}")
        
        print(f"Loaded {len(self.csv_games)} games from CSV")
        return self.csv_games
    
    def extract_game_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract game ID from Chess.com URL.
        
        Args:
            url: Chess.com game URL (e.g., https://www.chess.com/game/live/123456)
            
        Returns:
            Game ID string or None if not found
        """
        match = re.search(r'/game/live/(\d+)', url)
        return match.group(1) if match else None
    
    def extract_youtube_timestamp(self, url: str) -> Optional[int]:
        """
        Extract timestamp parameter from YouTube URL.
        
        Args:
            url: YouTube URL with timestamp (e.g., ?t=123 or &t=456)
            
        Returns:
            Timestamp in seconds or None if not found
        """
        match = re.search(r'[?&]t=(\d+)', url)
        return int(match.group(1)) if match else None
    
    def get_player_archives(self, username: str) -> List[str]:
        """
        Get all available monthly archive URLs for a Chess.com player.
        
        Chess.com organizes games by month. This method retrieves the list of
        all available monthly archive URLs for the specified player.
        
        Args:
            username: Chess.com username (e.g., "senseidanya", "hebeccararis")
            
        Returns:
            List of archive URLs (e.g., ["https://api.chess.com/pub/player/USER/games/2024/01", ...])
        """
        print(f"Fetching archives for player: {username}")
        
        url = f"https://api.chess.com/pub/player/{username}/games/archives"
        
        # Headers to mimic a real browser and avoid rate limiting
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.chess.com/',
        }
        
        # Hardcoded archive URLs for hebeccararis (Danya's main speedrun account)
        # Used as fallback if API request fails
        archive_urls = [
            "https://api.chess.com/pub/player/hebeccararis/games/2023/09",
            "https://api.chess.com/pub/player/hebeccararis/games/2023/10",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/02",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/03",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/04",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/05",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/06",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/07",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/08",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/09",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/10",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/11",
            "https://api.chess.com/pub/player/hebeccararis/games/2024/12",
            "https://api.chess.com/pub/player/hebeccararis/games/2025/01",
            "https://api.chess.com/pub/player/hebeccararis/games/2025/02",
            "https://api.chess.com/pub/player/hebeccararis/games/2025/03",
            "https://api.chess.com/pub/player/hebeccararis/games/2025/04",
            "https://api.chess.com/pub/player/hebeccararis/games/2025/05",
            "https://api.chess.com/pub/player/hebeccararis/games/2025/07",
            "https://api.chess.com/pub/player/hebeccararis/games/2025/10"
        ]
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            archives = data.get('archives', [])
            print(f"Found {len(archives)} archive months")
            return archives
        except Exception as e:
            print(f"Error fetching archives: {e}")
            print("Using fallback archive list")
            return archive_urls
    
    def search_archives_for_games(self, username: str, target_game_ids: List[str]) -> Dict[str, Dict]:
        """
        Search through player's monthly archives to find specific games.
        
        Args:
            username: Chess.com username
            target_game_ids: List of game IDs to search for
            
        Returns:
            Dictionary mapping game_id -> game data for found games
        """
        print(f"Searching archives for {len(target_game_ids)} target games...")
        
        archives = self.get_player_archives(username)
        found_games = {}
        
        # Headers for API requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.chess.com/',
        }
        
        # Search through each monthly archive
        for archive_url in archives:
            print(f"  Checking archive: {archive_url}")
            try:
                response = requests.get(archive_url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                games = data.get('games', [])
                
                print(f"    Found {len(games)} games in this archive")
                
                # Check each game in this archive
                for game in games:
                    game_url = game.get('url', '')
                    game_id = self.extract_game_id_from_url(game_url)
                    
                    if game_id in target_game_ids:
                        print(f"    ✓ MATCH FOUND: Game ID {game_id}")
                        found_games[game_id] = {
                            'game_data': game,
                            'archive_url': archive_url,
                            'found_in_archive': True
                        }
                        
            except Exception as e:
                print(f"    Error accessing archive {archive_url}: {e}")
        
        print(f"Found {len(found_games)} matches out of {len(target_game_ids)} target games")
        return found_games
    
    def match_csv_with_api(self, username: str = "hebeccararis") -> List[Dict]:
        """
        Main method to match CSV games with API data.
        
        Args:
            username: Chess.com username to search (default: hebeccararis - Danya's main account)
            
        Returns:
            List of match dictionaries containing:
                - csv_game: Original CSV data
                - api_game: Full game data from API (if found)
                - archive_url: Archive where game was found
                - match_status: "FOUND" or "NOT_FOUND"
        """
        print("=" * 60)
        print("CHESS GAME MATCHER")
        print("=" * 60)
        
        # Load CSV games
        csv_games = self.load_csv_games()
        if not csv_games:
            print("No CSV games loaded!")
            return []
        
        # Extract target game IDs to search for
        target_game_ids = [game['game_id'] for game in csv_games]
        print(f"Target game IDs: {target_game_ids[:5]}...")  # Show first 5
        
        # Search archives for these games
        found_games = self.search_archives_for_games(username, target_game_ids)
        
        # Create matches by combining CSV data with API data
        matches = []
        for csv_game in csv_games:
            game_id = csv_game['game_id']
            
            if game_id in found_games:
                match = {
                    'csv_game': csv_game,
                    'api_game': found_games[game_id]['game_data'],
                    'archive_url': found_games[game_id]['archive_url'],
                    'match_status': 'FOUND',
                    'youtube_url': csv_game['youtube_url'],
                    'youtube_timestamp': csv_game['youtube_timestamp']
                }
                matches.append(match)
                print(f"✓ MATCH: Game {game_id} found in archives")
            else:
                match = {
                    'csv_game': csv_game,
                    'api_game': None,
                    'archive_url': None,
                    'match_status': 'NOT_FOUND',
                    'youtube_url': csv_game['youtube_url'],
                    'youtube_timestamp': csv_game['youtube_timestamp']
                }
                matches.append(match)
                print(f"✗ NO MATCH: Game {game_id} not found in archives")
        
        self.matches = matches
        return matches
    
    def generate_match_report(self) -> str:
        """
        Generate a human-readable report of matching results.
        
        Returns:
            Formatted string with match statistics and details
        """
        if not self.matches:
            return "No matches to report"
        
        found_count = sum(1 for match in self.matches if match['match_status'] == 'FOUND')
        total_count = len(self.matches)
        
        report = f"""
CHESS GAME MATCHING REPORT
========================
Total CSV games: {total_count}
Found in API: {found_count}
Not found: {total_count - found_count}
Match rate: {(found_count/total_count)*100:.1f}%

DETAILED RESULTS:
"""
        
        for i, match in enumerate(self.matches, 1):
            csv_game = match['csv_game']
            status = match['match_status']
            
            report += f"\n{i}. Game ID: {csv_game['game_id']}\n"
            report += f"   Status: {status}\n"
            report += f"   YouTube: {csv_game['youtube_url']}\n"
            
            if status == 'FOUND':
                api_game = match['api_game']
                report += f"   Found in archive: {match['archive_url']}\n"
                report += f"   Game PGN preview: {api_game.get('pgn', '')[:100]}...\n"
            else:
                report += f"   NOT FOUND in any archive\n"
        
        return report
    
    def save_matches_to_file(self, filename: str = "game_matches.json"):
        """
        Save match results to JSON file for later processing.
        
        Args:
            filename: Output filename (default: game_matches.json)
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.matches, f, indent=2, ensure_ascii=False)
        print(f"✓ Matches saved to {filename}")


def main():
    """
    Main function to run the game matcher.
    
    Modify the CSV file path to process different speedrun series:
    - back_to_3000.csv
    - beginner_to_master.csv
    - develop_your_instincts.csv
    - master_class.csv
    - sensei_speedrun.csv
    - top_theory.csv
    """
    # Initialize matcher with CSV file
    matcher = ChessGameMatcher("../../data/csv/develop_your_instincts.csv")
    
    # Run the matching process
    matches = matcher.match_csv_with_api()
    
    # Generate and print report
    report = matcher.generate_match_report()
    print(report)
    
    # Save results to JSON file
    matcher.save_matches_to_file()
    
    return matches


if __name__ == "__main__":
    main()

