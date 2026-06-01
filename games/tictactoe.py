import copy
from typing import Dict, Any, List, Optional
from games.base import BaseGameBoard

class TicTacToeBoard(BaseGameBoard):
    """
    Tic-Tac-Toe Game Engine.
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        self.grid = [""] * 9
        self.current_turn = "X"
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "current_turn": self.current_turn
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.grid = copy.deepcopy(state.get("grid", [""] * 9))
        self.current_turn = state.get("current_turn", "X")
        
    def get_valid_moves(self, player: str) -> List[int]:
        if player != self.current_turn:
            return []
        if self.check_winner() is not None:
            return []
        return [i for i, cell in enumerate(self.grid) if cell == ""]
        
    def make_move(self, player: str, move: int) -> bool:
        if move in self.get_valid_moves(player):
            self.grid[move] = player
            self.current_turn = "O" if player == "X" else "X"
            return True
        return False
        
    def check_winner(self) -> Optional[str]:
        combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # cols
            [0, 4, 8], [2, 4, 6]             # diagonals
        ]
        for combo in combos:
            if self.grid[combo[0]] == self.grid[combo[1]] == self.grid[combo[2]] != "":
                return self.grid[combo[0]]
        if "" not in self.grid:
            return "draw"
        return None

    def get_board_visual(self) -> List[str]:
        return self.grid
