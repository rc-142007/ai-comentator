import copy
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class ReversiBoard(BaseGameBoard):
    """
    Reversi (Othello) 8x8 Board Game Engine.
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        self.grid = [["" for _ in range(8)] for _ in range(8)]
        # Initial 4 pieces in the center
        self.grid[3][3] = "O"
        self.grid[3][4] = "X"
        self.grid[4][3] = "X"
        self.grid[4][4] = "O"
        self.current_turn = "X" # X moves first
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "current_turn": self.current_turn
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.grid = copy.deepcopy(state.get("grid", [["" for _ in range(8)] for _ in range(8)]))
        self.current_turn = state.get("current_turn", "X")
        
    def get_valid_moves(self, player: str) -> List[Tuple[int, int]]:
        if player != self.current_turn:
            return []
            
        valid = []
        for r in range(8):
            for c in range(8):
                if self.grid[r][c] == "" and self._flips_any(r, c, player):
                    valid.append((r, c))
        return valid
        
    def make_move(self, player: str, move: Tuple[int, int]) -> bool:
        r, c = move
        valid_moves = self.get_valid_moves(player)
        if move in valid_moves:
            # Place piece
            self.grid[r][c] = player
            # Flip pieces in all directions
            self._flip_pieces(r, c, player)
            
            # Switch turn
            opponent = "O" if player == "X" else "X"
            self.current_turn = opponent
            
            # If opponent has no valid moves, switch back or end
            if not self.has_any_valid_moves(opponent):
                self.current_turn = player
                if not self.has_any_valid_moves(player):
                    self.current_turn = "" # Game over, no one can move
            return True
        return False
        
    def has_any_valid_moves(self, player: str) -> bool:
        for r in range(8):
            for c in range(8):
                if self.grid[r][c] == "" and self._flips_any(r, c, player):
                    return True
        return False
        
    def check_winner(self) -> Optional[str]:
        # If any player can still make a move, game is ongoing
        if self.has_any_valid_moves("X") or self.has_any_valid_moves("O"):
            return None
            
        # Count scores
        x_score = sum(row.count("X") for row in self.grid)
        o_score = sum(row.count("O") for row in self.grid)
        
        if x_score > o_score:
            return "X"
        elif o_score > x_score:
            return "O"
        else:
            return "draw"
            
    def _flips_any(self, r: int, c: int, player: str) -> bool:
        opponent = "O" if player == "X" else "X"
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for dr, dc in directions:
            curr_r, curr_c = r + dr, c + dc
            flipped_count = 0
            while 0 <= curr_r < 8 and 0 <= curr_c < 8 and self.grid[curr_r][curr_c] == opponent:
                curr_r += dr
                curr_c += dc
                flipped_count += 1
            if flipped_count > 0 and 0 <= curr_r < 8 and 0 <= curr_c < 8 and self.grid[curr_r][curr_c] == player:
                return True
        return False

    def _flip_pieces(self, r: int, c: int, player: str):
        opponent = "O" if player == "X" else "X"
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for dr, dc in directions:
            curr_r, curr_c = r + dr, c + dc
            to_flip = []
            while 0 <= curr_r < 8 and 0 <= curr_c < 8 and self.grid[curr_r][curr_c] == opponent:
                to_flip.append((curr_r, curr_c))
                curr_r += dr
                curr_c += dc
            if len(to_flip) > 0 and 0 <= curr_r < 8 and 0 <= curr_c < 8 and self.grid[curr_r][curr_c] == player:
                for fr, fc in to_flip:
                    self.grid[fr][fc] = player

    def get_board_visual(self) -> List[List[str]]:
        return self.grid
