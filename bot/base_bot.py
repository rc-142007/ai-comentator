from abc import ABC, abstractmethod
from typing import Any
from games.base import BaseGameBoard

class BaseGameBot(ABC):
    """
    Abstract interface for bot engines. Ensures bots can play any game registered.
    """
    @abstractmethod
    def select_move(self, game: BaseGameBoard, player: str, difficulty: str) -> Any:
        """
        Given the game board object, determine the best move.
        difficulty: "easy", "medium", or "hard".
        """
        pass
