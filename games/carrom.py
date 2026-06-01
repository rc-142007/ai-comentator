import copy
import random
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class CarromBoard(BaseGameBoard):
    """
    Carrom Board Game Engine (Tactical Grid-Based).
    Represented as a 5x5 board.
    - Corners (0,0), (0,4), (4,0), (4,4) are Pockets.
    - Pieces:
      - 'W': White Carrom men (worth 10 pts)
      - 'B': Black Carrom men (worth 10 pts)
      - 'Q': Red Queen (worth 25 pts)
      - '': Empty cell
    - Player 1 ('X') tries to pocket White pieces.
    - Player 2 ('O') tries to pocket Black pieces.
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        self.grid = [["" for _ in range(5)] for _ in range(5)]
        
        # Center setup
        self.grid[2][2] = "Q" # Queen in dead center
        self.grid[1][2] = "W"
        self.grid[3][2] = "W"
        self.grid[2][1] = "B"
        self.grid[2][3] = "B"
        
        self.current_turn = "X"
        self.scores = {"X": 0, "O": 0}
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "current_turn": self.current_turn,
            "scores": copy.deepcopy(self.scores)
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.grid = copy.deepcopy(state.get("grid", []))
        self.current_turn = state.get("current_turn", "X")
        self.scores = copy.deepcopy(state.get("scores", {"X": 0, "O": 0}))
        
    def get_valid_moves(self, player: str) -> List[Tuple[int, int]]:
        if player != self.current_turn:
            return []
        if self.check_winner() is not None:
            return []
            
        valid = []
        # A move is selecting any of the active pieces to 'strike' and push in a chosen direction
        for r in range(5):
            for c in range(5):
                # Cannot strike pockets
                if (r, c) in [(0,0), (0,4), (4,0), (4,4)]:
                    continue
                piece = self.grid[r][c]
                # Can strike White (for X), Black (for O), or the Queen (for either)
                if piece == "Q" or (player == "X" and piece == "W") or (player == "O" and piece == "B"):
                    # Choose a neighboring empty/valid cell to push it towards
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5:
                            valid.append(((r, c), (nr, nc)))
        return valid
        
    def make_move(self, player: str, move: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
        valid = self.get_valid_moves(player)
        if move not in valid:
            return False
            
        (sr, sc), (dr, dc) = move
        piece = self.grid[sr][sc]
        
        # Calculate push direction
        dr_dir, dc_dir = dr - sr, dc - sc
        
        # Move the piece in that direction until it hits wall, pocket, or another piece
        curr_r, curr_c = sr, sc
        self.grid[sr][sc] = ""
        
        next_r, next_c = curr_r + dr_dir, curr_c + dc_dir
        while 0 <= next_r < 5 and 0 <= next_c < 5:
            # Check pocket
            if (next_r, next_c) in [(0,0), (0,4), (4,0), (4,4)]:
                # Pocketed!
                self._resolve_pocket(player, piece)
                self.current_turn = "O" if player == "X" else "X"
                return True
                
            # Check collision with other piece
            if self.grid[next_r][next_c] != "":
                # Collides: push the other piece one cell further if possible
                self._push_piece(next_r, next_c, dr_dir, dc_dir, player)
                break
                
            curr_r, curr_c = next_r, next_c
            next_r += dr_dir
            next_c += dc_dir
            
        # Place piece at resting position
        self.grid[curr_r][curr_c] = piece
        self.current_turn = "O" if player == "X" else "X"
        return True
        
    def check_winner(self) -> Optional[str]:
        # Count remaining carrom men on board
        white_remaining = any("W" in row for row in self.grid)
        black_remaining = any("B" in row for row in self.grid)
        queen_remaining = any("Q" in row for row in self.grid)
        
        if not white_remaining and not black_remaining and not queen_remaining:
            if self.scores["X"] > self.scores["O"]:
                return "X"
            elif self.scores["O"] > self.scores["X"]:
                return "O"
            else:
                return "draw"
        return None
        
    def _resolve_pocket(self, player: str, piece: str):
        if piece == "W":
            self.scores["X"] += 10
        elif piece == "B":
            self.scores["O"] += 10
        elif piece == "Q":
            self.scores[player] += 25
            
    def _push_piece(self, r: int, c: int, dr: int, dc: int, player: str):
        piece = self.grid[r][c]
        nr, nc = r + dr, c + dc
        if 0 <= nr < 5 and 0 <= nc < 5:
            if (nr, nc) in [(0,0), (0,4), (4,0), (4,4)]:
                self._resolve_pocket(player, piece)
                self.grid[r][c] = ""
            elif self.grid[nr][nc] == "":
                self.grid[nr][nc] = piece
                self.grid[r][c] = ""
            else:
                # Recurse push
                self._push_piece(nr, nc, dr, dc, player)
                self.grid[nr][nc] = piece
                self.grid[r][c] = ""

    def get_board_visual(self) -> List[List[str]]:
        return self.grid
