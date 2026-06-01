import copy
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class TigerChessBoard(BaseGameBoard):
    """
    Tiger Chess (Bagh Chal / Tiger and Goats) 5x5 Board Game Engine.
    - Player 1 ('X'): Controls 4 Tigers ("T")
    - Player 2 ('O'): Controls 20 Goats ("G")
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        self.grid = [["" for _ in range(5)] for _ in range(5)]
        # Tigers start at the four corners
        self.grid[0][0] = "T"
        self.grid[0][4] = "T"
        self.grid[4][0] = "T"
        self.grid[4][4] = "T"
        
        self.goats_to_place = 20
        self.goats_captured = 0
        self.current_turn = "O" # Goats start by placing one goat
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "goats_to_place": self.goats_to_place,
            "goats_captured": self.goats_captured,
            "current_turn": self.current_turn
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.grid = copy.deepcopy(state.get("grid", [["" for _ in range(5)] for _ in range(5)]))
        self.goats_to_place = state.get("goats_to_place", 20)
        self.goats_captured = state.get("goats_captured", 0)
        self.current_turn = state.get("current_turn", "O")
        
    def get_valid_moves(self, player: str) -> List[Any]:
        if player != self.current_turn:
            return []
            
        valid = []
        # Goat turn ('O')
        if player == "O":
            if self.goats_to_place > 0:
                # Placing phase: Can place on any empty space
                for r in range(5):
                    for c in range(5):
                        if self.grid[r][c] == "":
                            valid.append((r, c))
            else:
                # Moving phase: Can move any goat to adjacent empty space
                for r in range(5):
                    for c in range(5):
                        if self.grid[r][c] == "G":
                            for nr, nc in self._get_adjacent(r, c):
                                if self.grid[nr][nc] == "":
                                    valid.append(((r, c), (nr, nc)))
                                    
        # Tiger turn ('X')
        elif player == "X":
            for r in range(5):
                for c in range(5):
                    if self.grid[r][c] == "T":
                        # Slides
                        for nr, nc in self._get_adjacent(r, c):
                            if self.grid[nr][nc] == "":
                                valid.append(((r, c), (nr, nc)))
                        # Jumps (Captures)
                        for nr, nc in self._get_adjacent(r, c):
                            if self.grid[nr][nc] == "G":
                                # Calculate jump direction
                                dr, dc = nr - r, nc - c
                                jr, jc = nr + dr, nc + dc
                                if 0 <= jr < 5 and 0 <= jc < 5 and self.grid[jr][jc] == "":
                                    valid.append(((r, c), (jr, jc)))
        return valid
        
    def make_move(self, player: str, move: Any) -> bool:
        valid = self.get_valid_moves(player)
        if move not in valid:
            return False
            
        if player == "O":
            # Placement phase
            if self.goats_to_place > 0:
                r, c = move
                self.grid[r][c] = "G"
                self.goats_to_place -= 1
            else:
                # Move phase
                (sr, sc), (dr, dc) = move
                self.grid[sr][sc] = ""
                self.grid[dr][dc] = "G"
        elif player == "X":
            (sr, sc), (dr, dc) = move
            # Check if this was a jump/capture
            if abs(dr - sr) == 2 or abs(dc - sc) == 2:
                # Captured goat coordinates
                cr = (sr + dr) // 2
                cc = (sc + dc) // 2
                self.grid[cr][cc] = ""
                self.goats_captured += 1
                
            self.grid[sr][sc] = ""
            self.grid[dr][dc] = "T"
            
        self.current_turn = "O" if player == "X" else "X"
        return True
        
    def check_winner(self) -> Optional[str]:
        # Tigers win if they capture 5 goats
        if self.goats_captured >= 5:
            return "X"
            
        # Goats win if tigers have zero legal moves
        if not self.get_valid_moves("X"):
            return "O"
            
        return None
        
    def _get_adjacent(self, r: int, c: int) -> List[Tuple[int, int]]:
        adj = []
        # Normal orthogonal steps
        orthogonal = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # Diagonals are allowed on intersections where r+c is even
        diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        steps = orthogonal
        if (r + c) % 2 == 0:
            steps += diagonals
            
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                adj.append((nr, nc))
        return adj

    def get_board_visual(self) -> List[List[str]]:
        return self.grid
