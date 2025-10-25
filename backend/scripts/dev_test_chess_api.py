#!/usr/bin/env python3
"""
DEVELOPMENT TOOL: Test Chess.com API Access
============================================

This is a development/testing script to verify Chess.com API connectivity.

Purpose:
--------
Before running the full pipeline, use this script to:
- Test if Chess.com API is accessible
- Verify you can fetch game data
- Check PGN format and move timestamps
- Debug API issues

This script is NOT part of the normal data pipeline - it's for debugging and development.

What It Tests:
--------------
1. Direct API access to a single game
2. Player archive access method
3. PGN parsing and position extraction
4. Clock time extraction from PGN comments
5. Web scraping as fallback (if API fails)

Usage:
------
    python dev_test_chess_api.py
    
Modify the test_url variable to test with different games.

Common Issues:
--------------
- 403 Forbidden: Chess.com may be rate limiting or blocking your IP
- 404 Not Found: Game ID doesn't exist or is private
- Timeout: Network issues or Chess.com is slow to respond

Solutions:
----------
- Add delays between requests (already implemented)
- Use proper User-Agent headers (already implemented)
- Try the player archive approach instead of direct game access
- Consider using Lichess API as an alternative (no rate limits)
"""

import requests
import json
import re
from datetime import datetime
import chess
import chess.pgn
from io import StringIO

def extract_game_id_from_url(url):
    """
    Extract game ID from Chess.com URL.
    
    Args:
        url: Chess.com game URL
        
    Returns:
        Game ID string or None
        
    Example:
        extract_game_id_from_url("https://www.chess.com/game/live/123456") -> "123456"
    """
    match = re.search(r'/game/live/(\d+)', url)
    return match.group(1) if match else None

def fetch_game_data(game_id):
    """
    Fetch game data from Chess.com API using multiple methods.
    
    Tries different endpoints:
    1. Direct game API: /pub/game/{id}
    2. PGN endpoint: /pub/game/{id}/pgn
    
    Args:
        game_id: Chess.com game ID
        
    Returns:
        Dictionary with game data, or None if all methods fail
    """
    endpoints = [
        f"https://api.chess.com/pub/game/{game_id}",
        f"https://api.chess.com/pub/game/{game_id}/pgn",
    ]
    
    # Headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.chess.com/',
    }
    
    for i, url in enumerate(endpoints):
        try:
            print(f"Trying endpoint: {url}")
            
            # Add delay between requests to avoid rate limiting
            if i > 0:
                import time
                print("Waiting 2 seconds to avoid rate limiting...")
                time.sleep(2)
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                if url.endswith('/pgn'):
                    # PGN endpoint returns plain text
                    return {'pgn': response.text}
                else:
                    # JSON endpoint
                    return response.json()
            elif response.status_code == 403:
                print("403 Forbidden - possible IP blocking or rate limiting")
                print("Response headers:", dict(response.headers))
            else:
                error_preview = response.text[:200] if response.text else "[No response body]"
                print(f"Failed with status {response.status_code}: {error_preview}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error with {url}: {e}")
    
    return None

def parse_pgn_to_fen_positions(pgn_string):
    """
    Parse PGN and generate FEN positions for each move.
    
    Args:
        pgn_string: PGN text
        
    Returns:
        List of position dictionaries with move number, FEN, and move
    """
    pgn_io = StringIO(pgn_string)
    game = chess.pgn.read_game(pgn_io)
    
    if not game:
        return []
    
    board = game.board()
    positions = []
    
    # Add initial position
    positions.append({
        'move_number': 0,
        'fen': board.fen(),
        'move': None,
        'time': None
    })
    
    # Iterate through all moves
    move_number = 1
    for move in game.mainline_moves():
        board.push(move)
        positions.append({
            'move_number': move_number,
            'fen': board.fen(),
            'move': str(move),
            'time': None
        })
        move_number += 1
    
    return positions

def extract_timestamps_from_pgn(pgn_string):
    """
    Extract move timestamps from PGN comments.
    
    Chess.com PGNs include clock times like: {[%clk 0:05:30]}
    
    Args:
        pgn_string: PGN text
        
    Returns:
        List of timestamps in seconds
    """
    # Pattern: {[%clk H:MM:SS]} or {[%clk H:MM:SS.f]}
    timestamp_pattern = r'\{\[%clk\s+(\d+):(\d+):([\d.]+)\]\}'
    timestamps = []
    
    for line in pgn_string.split('\n'):
        matches = re.findall(timestamp_pattern, line)
        for match in matches:
            hours, minutes, seconds = map(float, match)
            total_seconds = hours * 3600 + minutes * 60 + seconds
            timestamps.append(total_seconds)
    
    return timestamps

def try_player_archive_approach(target_game_id):
    """
    Try to access game through player's monthly archive.
    
    This is often more reliable than direct game access.
    
    Args:
        target_game_id: Game ID to search for
        
    Returns:
        Game data dictionary or None
    """
    print("\n" + "="*60)
    print("Trying player archive approach...")
    print("="*60)
    
    username = "senseidanya"  # Danya's main account
    archive_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        print(f"Fetching archives from: {archive_url}")
        response = requests.get(archive_url, headers=headers, timeout=10)
        print(f"Archive response status: {response.status_code}")
        
        if response.status_code == 200:
            archives = response.json()
            archive_list = archives.get('archives', [])
            print(f"Found {len(archive_list)} archive months")
            
            # Search through recent archives
            for archive_url in archive_list[-3:]:  # Check last 3 months
                print(f"\nChecking archive: {archive_url}")
                
                games_response = requests.get(archive_url, headers=headers, timeout=10)
                if games_response.status_code == 200:
                    games_data = games_response.json()
                    games = games_data.get('games', [])
                    print(f"  Found {len(games)} games in this archive")
                    
                    # Show sample games
                    if games:
                        print(f"  Sample game URLs:")
                        for i, game in enumerate(games[:3]):
                            print(f"    {i+1}. {game.get('url', 'N/A')}")
                    
                    # Search for target game
                    for game in games:
                        if target_game_id in str(game.get('url', '')):
                            print(f"\n✓ Found target game {target_game_id} in archive!")
                            return game
                else:
                    print(f"  Failed to access archive: {games_response.status_code}")
            
            print(f"\n✗ Game {target_game_id} not found in recent archives")
        
        return None
        
    except Exception as e:
        print(f"Error with player archive approach: {e}")
        return None

def test_chess_api():
    """
    Main test function - tests various methods of accessing Chess.com game data.
    """
    print("\n" + "="*80)
    print("  CHESS.COM API TEST TOOL")
    print("="*80)
    
    # Test game (modify this to test different games)
    test_url = "https://www.chess.com/game/live/144609732618"
    youtube_url = "https://youtu.be/EXAMPLE?t=123"
    
    print(f"\nTest game URL: {test_url}")
    print(f"Corresponding YouTube: {youtube_url}")
    print("-" * 80)
    
    # Extract game ID
    game_id = extract_game_id_from_url(test_url)
    if not game_id:
        print("✗ Could not extract game ID from URL")
        return
    
    print(f"✓ Extracted game ID: {game_id}\n")
    
    # Method 1: Direct API access
    print("METHOD 1: Direct API Access")
    print("-" * 80)
    game_data = fetch_game_data(game_id)
    
    # Method 2: Player archive access
    if not game_data:
        print("\nMETHOD 2: Player Archive Access")
        print("-" * 80)
        game_data = try_player_archive_approach(game_id)
    
    # Check results
    if not game_data:
        print("\n" + "="*80)
        print("✗ ALL METHODS FAILED")
        print("="*80)
        print("\nPossible causes:")
        print("  - Chess.com is blocking automated access")
        print("  - Game is private or doesn't exist")
        print("  - Rate limiting is active")
        print("\nAlternative approaches:")
        print("  1. Use Chess.com's official API with authentication")
        print("  2. Switch to Lichess API (no rate limits)")
        print("  3. Manually download PGN files")
        print("="*80)
        return
    
    # Success! Analyze the game data
    print("\n" + "="*80)
    print("✓ SUCCESS! Game data retrieved")
    print("="*80)
    print(f"\nGame data keys: {list(game_data.keys())}")
    
    # Display PGN analysis if available
    if 'pgn' in game_data:
        pgn = game_data['pgn']
        print(f"\n✓ PGN found! Length: {len(pgn)} characters")
        print("\nFirst 500 characters of PGN:")
        print("-" * 80)
        print(pgn[:500])
        print("-" * 80)
        
        # Parse positions
        print("\nParsing PGN to extract positions...")
        positions = parse_pgn_to_fen_positions(pgn)
        print(f"✓ Extracted {len(positions)} positions")
        
        # Show sample positions
        print("\nFirst 5 positions:")
        for pos in positions[:5]:
            print(f"  Move {pos['move_number']}: {pos['move']} -> {pos['fen'][:50]}...")
        
        # Extract timestamps
        timestamps = extract_timestamps_from_pgn(pgn)
        print(f"\n✓ Found {len(timestamps)} timestamps in PGN")
        if timestamps:
            print(f"  Sample timestamps: {timestamps[:5]}")
    
    # Display other available data
    print("\nOther available data:")
    print("-" * 80)
    for key, value in game_data.items():
        if key != 'pgn':  # Already showed PGN
            if isinstance(value, (str, int, float)):
                print(f"  {key}: {value}")
            elif isinstance(value, dict):
                print(f"  {key}: {list(value.keys())}")
            else:
                print(f"  {key}: {type(value)}")
    
    print("\n" + "="*80)
    print("✓ TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_chess_api()

