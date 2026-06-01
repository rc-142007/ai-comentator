import sqlite3
import json
from typing import Dict, Any, List, Optional

class GameDatabase:
    """
    A lightweight, robust database coordinator built with SQLite.
    Handles users, stats, ELOs, active rooms, match logs, and bot telemetry.
    """
    def __init__(self, db_path: str = "crt_games.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users & Ratings Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    avatar_emoji TEXT,
                    elo INTEGER DEFAULT 1200
                )
            """)
            
            # Matches History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id TEXT PRIMARY KEY,
                    game_id TEXT,
                    player_1 TEXT,
                    player_2 TEXT,
                    winner TEXT,
                    total_moves INTEGER,
                    duration_seconds INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Bot Telemetry Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_telemetry (
                    game_id TEXT,
                    difficulty TEXT,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    PRIMARY KEY (game_id, difficulty)
                )
            """)
            
            # Seed default users
            cursor.execute("INSERT OR IGNORE INTO users (user_id, username, avatar_emoji, elo) VALUES ('user_1', 'Challenger', '🦊', 1200)")
            cursor.execute("INSERT OR IGNORE INTO users (user_id, username, avatar_emoji, elo) VALUES ('user_2', 'Grandmaster', '🦁', 1500)")
            
            conn.commit()
            
    def get_user_elo(self, username: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT elo FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return row[0]
            # Create user if not existing
            cursor.execute("INSERT INTO users (user_id, username, avatar_emoji, elo) VALUES (?, ?, ?, 1200)", 
                           (username.lower(), username, "👤"))
            conn.commit()
            return 1200

    def update_user_elo(self, username: str, new_elo: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET elo = ? WHERE username = ?", (new_elo, username))
            conn.commit()
            
    def record_match(self, match_id: str, game_id: str, player_1: str, player_2: str, winner: str, total_moves: int, duration_sec: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO matches (match_id, game_id, player_1, player_2, winner, total_moves, duration_seconds) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (match_id, game_id, player_1, player_2, winner, total_moves, duration_sec))
            conn.commit()

    def get_match_history(self, game_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if game_id:
                cursor.execute("SELECT match_id, game_id, player_1, player_2, winner, completed_at FROM matches WHERE game_id = ? ORDER BY completed_at DESC LIMIT 10", (game_id,))
            else:
                cursor.execute("SELECT match_id, game_id, player_1, player_2, winner, completed_at FROM matches ORDER BY completed_at DESC LIMIT 10")
            
            rows = cursor.fetchall()
            return [
                {
                    "match_id": r[0],
                    "game_id": r[1],
                    "player_1": r[2],
                    "player_2": r[3],
                    "winner": r[4],
                    "completed_at": r[5]
                }
                for r in rows
            ]

    def record_bot_game(self, game_id: str, difficulty: str, outcome: str):
        """outcome can be 'win', 'loss', or 'draw' (from bot's perspective)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO bot_telemetry (game_id, difficulty, wins, losses, draws) VALUES (?, ?, 0, 0, 0)", (game_id, difficulty))
            if outcome == 'win':
                cursor.execute("UPDATE bot_telemetry SET wins = wins + 1 WHERE game_id = ? AND difficulty = ?", (game_id, difficulty))
            elif outcome == 'loss':
                cursor.execute("UPDATE bot_telemetry SET losses = losses + 1 WHERE game_id = ? AND difficulty = ?", (game_id, difficulty))
            else:
                cursor.execute("UPDATE bot_telemetry SET draws = draws + 1 WHERE game_id = ? AND difficulty = ?", (game_id, difficulty))
            conn.commit()

    def get_bot_stats(self, game_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT difficulty, wins, losses, draws FROM bot_telemetry WHERE game_id = ?", (game_id,))
            rows = cursor.fetchall()
            return [
                {"difficulty": r[0], "wins": r[1], "losses": r[2], "draws": r[3]}
                for r in rows
            ]

    def get_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM matches")
            total = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM matches WHERE winner = 'X'")
            wins = cursor.fetchone()[0] or 0
            return {"total_matches": total, "human_wins": wins}
