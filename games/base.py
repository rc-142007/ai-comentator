from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseGameBoard(ABC):
    """
    Abstract Base Class that every board game in the platform MUST implement.
    Allows the FastAPI backend and Streamlit frontend to interact with any game
    generically without knowing details of its rules.
    """
    
    @abstractmethod
    def reset(self) -> None:
        """Resets the board state back to the start state."""
        pass
        
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Returns a serializable dictionary representing the exact board state."""
        pass
        
    @abstractmethod
    def set_state(self, state: Dict[str, Any]) -> None:
        """Sets the board state from a serializable state dictionary."""
        pass
        
    @abstractmethod
    def get_valid_moves(self, player: str) -> List[Any]:
        """Returns a list of valid moves for the specified player."""
        pass
        
    @abstractmethod
    def make_move(self, player: str, move: Any) -> bool:
        """
        Executes a move. 
        Returns True if the move is valid and successfully played, False otherwise.
        """
        pass
        
    @abstractmethod
    def check_winner(self) -> Optional[str]:
        """Returns the winning player symbol/ID ('X', 'O', '1', '2'), 'draw', or None if game is ongoing."""
        pass

    @abstractmethod
    def get_board_visual(self) -> Any:
        """Returns a structure optimized for UI rendering (e.g., list, matrix, dict)."""
        pass
