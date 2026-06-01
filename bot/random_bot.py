import random
from typing import Any
from bot.base_bot import BaseGameBot
from games.base import BaseGameBoard

class RandomBot(BaseGameBot):
    """
    A basic bot that selects moves randomly from the list of valid moves.
    Serves as an robust fallback and an 'easy' mode bot for all games.
    """
    def select_move(self, game: BaseGameBoard, player: str, difficulty: str = "easy") -> Any:
        valid_moves = game.get_valid_moves(player)
        if not valid_moves:
            return None
        return random.choice(valid_moves)
