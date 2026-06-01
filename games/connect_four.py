import copy
from typing import Dict, Any, List, Optional
from games.base import BaseGameBoard

class ConnectFourBoard(BaseGameBoard):
    """
    Connect Four Game Engine (7 columns x 6 rows).
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        # 6 rows, 7 columns, initialized to ""
        self.grid = [["" for _ in range(7)] for _ in range(6)]
        self.current_turn = "X" # X is Player 1, O is Player 2
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "current_turn": self.current_turn
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.grid = copy.deepcopy(state.get("grid", [["" for _ in range(7)] for _ in range(6)]))
        self.current_turn = state.get("current_turn", "X")
        
    def get_valid_moves(self, player: str) -> List[int]:
        if player != self.current_turn:
            return []
        if self.check_winner() is not None:
            return []
        # Columns that have at least one empty cell at the top row (row 0)
        return [c for c in range(7) if self.grid[0][c] == ""]
        
    def make_move(self, player: str, move: int) -> bool:
        # Move is a column index (0-6)
        if move in self.get_valid_moves(player):
            # Drop the piece to the lowest available row in column 'move'
            for r in range(5, -1, -1):
                if self.grid[r][move] == "":
                    self.grid[r][move] = player
                    self.current_turn = "O" if player == "X" else "X"
                    return True
        return False
        
    def check_winner(self) -> Optional[str]:
        # Check horizontal wins
        for r in range(6):
            for c in range(4):
                if self.grid[r][c] == self.grid[r][c+1] == self.grid[r][c+2] == self.grid[r][c+3] != "":
                    return self.grid[r][c]
                    
        # Check vertical wins
        for r in range(3):
            for c in range(7):
                if self.grid[r][c] == self.grid[r+1][c] == self.grid[r+2][c] == self.grid[r+3][c] != "":
                    return self.grid[r][c]
                    
        # Check positively sloped diagonals
        for r in range(3, 6):
            for c in range(4):
                if self.grid[r][c] == self.grid[r-1][c+1] == self.grid[r-2][c+2] == self.grid[r-3][c+3] != "":
                    return self.grid[r][c]
                    
        # Check negatively sloped diagonals
        for r in range(3):
            for c in range(4):
                if self.grid[r][c] == self.grid[r+1][c+1] == self.grid[r+2][c+2] == self.grid[r+3][c+3] != "":
                    return self.grid[r][c]
                    
        # Check for draw (full board)
        if all(self.grid[0][c] != "" for c in range(7)):
            return "draw"
            
        return None

    def get_board_visual(self) -> List[List[str]]:
        return self.grid
