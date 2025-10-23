#!/usr/bin/env python3
"""
Test script to fetch game data from Chess.com API for one of Daniel Naroditsky's games.
This will help determine if we can get all the data needed for the position matching application.
"""

import requests
import json
import re
from datetime import datetime
import chess
import chess.pgn
from io import StringIO

def extract_game_id_from_url(url):
    """Extract game ID from Chess.com URL"""
    # Pattern: https://www.chess.com/game/live/{game_id}?username=...
    match = re.search(r'/game/live/(\d+)', url)
    return match.group(1) if match else None

def fetch_game_data(game_id):
    """Fetch game data from Chess.com API"""
    # Try different endpoints with proper headers and delays
    endpoints = [
        f"https://api.chess.com/pub/game/{game_id}",
        f"https://api.chess.com/pub/game/{game_id}/pgn",
    ]
    
    # Headers to mimic a real browser
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
                try:
                    error_text = response.text[:200]
                    print(f"Failed with status {response.status_code}: {error_text}")
                except UnicodeEncodeError:
                    print(f"Failed with status {response.status_code}: [Unable to display response text due to encoding]")
                
        except requests.exceptions.RequestException as e:
            print(f"Error with {url}: {e}")
    
    return None

def parse_pgn_to_fen_positions(pgn_string):
    """Parse PGN and generate FEN positions for each move"""
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
    
    move_number = 1
    for move in game.mainline_moves():
        board.push(move)
        positions.append({
            'move_number': move_number,
            'fen': board.fen(),
            'move': str(move),
            'time': None  # We'll need to extract this from the PGN headers
        })
        move_number += 1
    
    return positions

def extract_timestamps_from_pgn(pgn_string):
    """Extract move timestamps from PGN string"""
    # Look for timestamp patterns in the PGN
    # Chess.com PGNs often have timestamps in format like {[%clk 0:05:30]}
    timestamp_pattern = r'\{\[%clk\s+(\d+):(\d+):(\d+)\]\}'
    timestamps = []
    
    lines = pgn_string.split('\n')
    for line in lines:
        matches = re.findall(timestamp_pattern, line)
        for match in matches:
            hours, minutes, seconds = map(int, match)
            total_seconds = hours * 3600 + minutes * 60 + seconds
            timestamps.append(total_seconds)
    
    return timestamps

def try_player_archive_approach(target_game_id):
    """Try to access games through player archive"""
    print("Trying player archive approach...")
    
    # Try to get Daniel Naroditsky's game archives
    username = "senseidanya"  # From the CSV URLs
    archive_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    
    # Headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.chess.com/',
    }
    
    try:
        print(f"Fetching archives from: {archive_url}")
        response = requests.get(archive_url, headers=headers, timeout=10)
        print(f"Archive response status: {response.status_code}")
        
        if response.status_code == 200:
            archives = response.json()
            print(f"Found {len(archives.get('archives', []))} archive months")
            
            # Try to get games from multiple archives (starting with most recent)
            if archives.get('archives'):
                
                # Search through the last few archives
                for archive_url in archives['archives'][-3:]:  # Check last 3 archives
                    print(f"Trying archive: {archive_url}")
                    
                    games_response = requests.get(archive_url, headers=headers, timeout=10)
                    if games_response.status_code == 200:
                        games_data = games_response.json()
                        print(f"Found {len(games_data.get('games', []))} games in this archive")
                        
                        # Look for our specific game and show some sample games
                        games = games_data.get('games', [])
                        print(f"Sample game URLs from this archive:")
                        for i, game in enumerate(games[:3]):  # Show first 3 games
                            print(f"  {i+1}. {game.get('url', 'N/A')}")
                        
                        for game in games:
                            if str(game.get('url', '')).endswith(target_game_id):
                                print("Found target game in archive!")
                                return game
                    else:
                        print(f"Failed to access archive: {games_response.status_code}")
                        
                print(f"Game {target_game_id} not found in recent archives")
                            
        return None
        
    except Exception as e:
        print(f"Error with player archive approach: {e}")
        return None

def test_web_scraping_approach():
    """Try to get game data through web scraping"""
    print("Trying web scraping approach...")
    
    # Try to access the game page directly
    game_url = "https://www.chess.com/game/live/144609732618"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(game_url, headers=headers)
        print(f"Web scraping response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"HTML content length: {len(content)} characters")
            
            # Look for various chess-related data in the HTML
            chess_indicators = ['pgn', 'fen', 'chess', 'board', 'moves', 'game']
            found_indicators = []
            
            for indicator in chess_indicators:
                if indicator in content.lower():
                    found_indicators.append(indicator)
            
            print(f"Found chess-related indicators: {found_indicators}")
            
            # Look for JSON data that might contain game information
            import re
            json_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
            json_match = re.search(json_pattern, content)
            
            if json_match:
                print("Found potential game data in window.__INITIAL_STATE__")
                try:
                    import json
                    game_data = json.loads(json_match.group(1))
                    print(f"Game data keys: {list(game_data.keys()) if isinstance(game_data, dict) else 'Not a dict'}")
                    return True
                except json.JSONDecodeError:
                    print("Could not parse JSON data")
            
            # Look for other potential data sources
            if 'pgn' in content.lower():
                print("Found PGN data in HTML response")
                return True
            else:
                print("No obvious PGN data found in HTML")
                # Show a sample of the HTML content
                print("HTML sample (first 500 chars):")
                print(content[:500])
                return False
        else:
            print(f"Failed to access game page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error with web scraping: {e}")
        return False

def test_chess_api():
    """Test the Chess.com API with one game from the CSV"""
    
    # Test with the provided game ID
    test_url = "https://www.chess.com/game/live/144609732618"
    youtube_url = "Test game from user"
    
    print(f"Testing with game URL: {test_url}")
    print(f"Corresponding YouTube URL: {youtube_url}")
    print("-" * 80)
    
    # Extract game ID
    game_id = extract_game_id_from_url(test_url)
    if not game_id:
        print("Could not extract game ID from URL")
        return
    
    print(f"Extracted game ID: {game_id}")
    
    # Fetch game data
    print("Fetching game data from Chess.com API...")
    game_data = fetch_game_data(game_id)
    
    if not game_data:
        print("Failed to fetch game data directly, trying player archive approach...")
        game_data = try_player_archive_approach(game_id)
    
    if not game_data:
        print("Failed to fetch game data through API methods, trying web scraping...")
        web_scraping_success = test_web_scraping_approach()
        if not web_scraping_success:
            print("All methods failed - Chess.com may be blocking automated access")
            print("\nAlternative approaches to consider:")
            print("1. Use Chess.com's official API with proper authentication")
            print("2. Use a different chess database (like Lichess API)")
            print("3. Manually download PGN files and process them")
            print("4. Use a chess library that can parse game URLs")
            return
    
    print("Successfully fetched game data!")
    print(f"Game data keys: {list(game_data.keys())}")
    print("-" * 80)
    
    # Display basic game information
    if 'pgn' in game_data:
        print("PGN found in response!")
        pgn = game_data['pgn']
        print(f"PGN length: {len(pgn)} characters")
        print("First 500 characters of PGN:")
        print(pgn[:500])
        print("-" * 80)
        
        # Parse PGN to get positions
        print("Parsing PGN to extract positions...")
        positions = parse_pgn_to_fen_positions(pgn)
        print(f"Found {len(positions)} positions")
        
        # Show first few positions
        print("First 5 positions:")
        for i, pos in enumerate(positions[:5]):
            print(f"  Move {pos['move_number']}: {pos['move']} -> {pos['fen'][:50]}...")
        
        # Extract timestamps
        timestamps = extract_timestamps_from_pgn(pgn)
        print(f"Found {len(timestamps)} timestamps in PGN")
        if timestamps:
            print(f"First few timestamps: {timestamps[:5]}")
    
    # Display other available data
    print("\nOther available data:")
    for key, value in game_data.items():
        if key != 'pgn':  # We already showed PGN
            if isinstance(value, (str, int, float)):
                print(f"  {key}: {value}")
            elif isinstance(value, dict):
                print(f"  {key}: {list(value.keys())}")
            else:
                print(f"  {key}: {type(value)}")

if __name__ == "__main__":
    test_chess_api()
