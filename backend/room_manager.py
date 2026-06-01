import uuid
from typing import Dict, List, Optional
from fastapi import WebSocket
from games.game_registry import get_game_instance
from games.base import BaseGameBoard

class Room:
    def __init__(self, room_id: str, game_id: str):
        self.room_id = room_id
        self.game_id = game_id
        self.game: BaseGameBoard = get_game_instance(game_id)
        self.clients: Dict[str, WebSocket] = {} # player_id -> WebSocket
        self.player_symbols: Dict[str, str] = {} # player_id -> "X" or "O"

    def add_player(self, player_id: str, websocket: WebSocket) -> str:
        self.clients[player_id] = websocket
        if len(self.player_symbols) == 0:
            self.player_symbols[player_id] = "X"
        elif len(self.player_symbols) == 1:
            # Assign opposite symbol
            existing_symbol = list(self.player_symbols.values())[0]
            self.player_symbols[player_id] = "O" if existing_symbol == "X" else "X"
        else:
            # Spectator
            self.player_symbols[player_id] = "Spectator"
        return self.player_symbols[player_id]

    def remove_player(self, player_id: str):
        if player_id in self.clients:
            del self.clients[player_id]


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    def create_room(self, game_id: str) -> str:
        room_code = str(uuid.uuid4())[:6].upper() # 6-digit easy code e.g., AB3D8E
        self.rooms[room_code] = Room(room_code, game_id)
        return room_code

    def get_room(self, room_code: str) -> Optional[Room]:
        return self.rooms.get(room_code.upper())

    def close_room(self, room_code: str):
        code = room_code.upper()
        if code in self.rooms:
            del self.rooms[code]
