import copy
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class HexBoard(BaseGameBoard):
    """
    Hex Board Game Engine (5x5 Grid).
    - Player 1 ('X'): Connects TOP to BOTTOM.
    - Player 2 ('O'): Connects LEFT to RIGHT.
    """
    def __init__(self, size: int = 5):
        self.size = size
        self.reset()
        
    def reset(self) -> None:
        self.grid = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.current_turn = "X"
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "current_turn": self.current_turn,
            "size": self.size
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.size = state.get("size", 5)
        self.grid = copy.deepcopy(state.get("grid", [["" for _ in range(self.size)] for _ in range(self.size)]))
        self.current_turn = state.get("current_turn", "X")
        
    def get_valid_moves(self, player: str) -> List[Tuple[int, int]]:
        if player != self.current_turn:
            return []
        if self.check_winner() is not None:
            return []
            
        valid = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == "":
                    valid.append((r, c))
        return valid
        
    def make_move(self, player: str, move: Tuple[int, int]) -> bool:
        if move in self.get_valid_moves(player):
            r, c = move
            self.grid[r][c] = player
            self.current_turn = "O" if player == "X" else "X"
            return True
        return False
        
    def check_winner(self) -> Optional[str]:
        # 1. Check if 'X' (Top to Bottom) connected
        if self._has_connected_top_to_bottom("X"):
            return "X"
        # 2. Check if 'O' (Left to Right) connected
        if self._has_connected_left_to_right("O"):
            return "O"
        return None
        
    def _get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        # Hexagonal grid connectivity
        offsets = [
            (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0)
        ]
        neighbors = []
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors.append((nr, nc))
        return neighbors
        
    def _has_connected_top_to_bottom(self, player: str) -> bool:
        # Starting nodes are the top row cells that are occupied by the player
        queue = [(0, c) for c in range(self.size) if self.grid[0][c] == player]
        visited = set(queue)
        
        while queue:
            r, c = queue.pop(0)
            if r == self.size - 1:
                return True
                
            for nr, nc in self._get_neighbors(r, c):
                if self.grid[nr][nc] == player and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return False
        
    def _has_connected_left_to_right(self, player: str) -> bool:
        # Starting nodes are the left column cells occupied by the player
        queue = [(r, 0) for r in range(self.size) if self.grid[r][0] == player]
        visited = set(queue)
        
        while queue:
            r, c = queue.pop(0)
            if c == self.size - 1:
                return True
                
            for nr, nc in self._get_neighbors(r, c):
                if self.grid[nr][nc] == player and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return False

    def get_board_visual(self) -> List[List[str]]:
        return self.grid
