from abc import ABC, abstractmethod
from typing import Dict, Any
from games.base import BaseGameBoard

class BaseAICommentator(ABC):
    """
    Generates live, highly engaging commentary text based on recent moves.
    """
    @abstractmethod
    def generate_commentary(self, game: BaseGameBoard, last_move: Any, last_player: str) -> Dict[str, Any]:
        """
        Analyzes the state change and returns commentary details:
        {
           "text": "Unbelievable play! A true game-changer...",
           "sentiment": "excited" | "mocking" | "analytical",
           "avatar_reaction": "😲" | "😂" | "🤔"
        }
        """
        pass
