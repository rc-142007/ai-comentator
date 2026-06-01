import copy
from typing import Dict, Any, List, Optional, Tuple, Set
from games.base import BaseGameBoard

class GoBoard(BaseGameBoard):
    """
    Go (Weiqi) Game Engine (9x9 Grid).
    """
    def __init__(self, size: int = 9):
        self.size = size
        self.reset()
        
    def reset(self) -> None:
        self.grid = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.current_turn = "X" # X represents Black (moves first), O represents White
        self.passes = 0
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "current_turn": self.current_turn,
            "passes": self.passes
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.grid = copy.deepcopy(state.get("grid", [["" for _ in range(self.size)] for _ in range(self.size)]))
        self.current_turn = state.get("current_turn", "X")
        self.passes = state.get("passes", 0)
        
    def get_valid_moves(self, player: str) -> List[Tuple[int, int]]:
        if player != self.current_turn:
            return []
        if self.passes >= 2:
            return []
            
        valid = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == "":
                    # Test suicide rule: A move must have liberties or capture opponent
                    if self._is_valid_move(r, c, player):
                        valid.append((r, c))
        return valid
        
    def make_move(self, player: str, move: Any) -> bool:
        # Move can be (row, col) or "pass"
        if move == "pass":
            self.passes += 1
            self.current_turn = "O" if player == "X" else "X"
            return True
            
        if move in self.get_valid_moves(player):
            r, c = move
            self.grid[r][c] = player
            self.passes = 0
            
            # Resolve captures
            self._capture_opponents(r, c, player)
            
            # Switch turn
            self.current_turn = "O" if player == "X" else "X"
            return True
        return False
        
    def check_winner(self) -> Optional[str]:
        # If both pass consecutively, the game ends
        if self.passes >= 2:
            # Count territory & pieces
            x_score = sum(row.count("X") for row in self.grid)
            o_score = sum(row.count("O") for row in self.grid)
            if x_score > o_score:
                return "X"
            elif o_score > x_score:
                return "O"
            else:
                return "draw"
        return None
        
    def _is_valid_move(self, r: int, c: int, player: str) -> bool:
        # Temporarily place stone
        self.grid[r][c] = player
        has_liberties = self._get_liberties(r, c, player) > 0
        
        # If it has liberties, it's valid
        if has_liberties:
            self.grid[r][c] = ""
            return True
            
        # Check if it captures any opponent groups
        opponent = "O" if player == "X" else "X"
        neighbors = self._get_neighbors(r, c)
        captures_any = False
        for nr, nc in neighbors:
            if self.grid[nr][nc] == opponent:
                if self._get_liberties(nr, nc, opponent) == 0:
                    captures_any = True
                    break
                    
        self.grid[r][c] = ""
        return captures_any
        
    def _get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors.append((nr, nc))
        return neighbors
        
    def _get_group(self, r: int, c: int, player: str) -> Set[Tuple[int, int]]:
        group = {(r, c)}
        queue = [(r, c)]
        while queue:
            curr_r, curr_c = queue.pop(0)
            for nr, nc in self._get_neighbors(curr_r, curr_c):
                if self.grid[nr][nc] == player and (nr, nc) not in group:
                    group.add((nr, nc))
                    queue.append((nr, nc))
        return group
        
    def _get_liberties(self, r: int, c: int, player: str) -> int:
        group = self._get_group(r, c, player)
        liberties = set()
        for gr, gc in group:
            for nr, nc in self._get_neighbors(gr, gc):
                if self.grid[nr][nc] == "":
                    liberties.add((nr, nc))
        return len(liberties)
        
    def _capture_opponents(self, r: int, c: int, player: str):
        opponent = "O" if player == "X" else "X"
        neighbors = self._get_neighbors(r, c)
        for nr, nc in neighbors:
            if self.grid[nr][nc] == opponent:
                if self._get_liberties(nr, nc, opponent) == 0:
                    # Remove the captured stones
                    opponent_group = self._get_group(nr, nc, opponent)
                    for gr, gc in opponent_group:
                        self.grid[gr][gc] = ""

    def get_board_visual(self) -> List[List[str]]:
        return self.grid
