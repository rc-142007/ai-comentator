import copy
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class CheckersBoard(BaseGameBoard):
    """
    Standard Checkers (8x8) Board Game Engine.
    Pieces:
    - "X": Player 1 regular piece
    - "XK": Player 1 King
    - "O": Player 2 regular piece
    - "OK": Player 2 King
    - "": Empty cell
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        self.grid = [["" for _ in range(8)] for _ in range(8)]
        # Populate Player 2 ("O") pieces in top 3 rows (on dark squares: r+c is odd)
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 != 0:
                    self.grid[r][c] = "O"
                    
        # Populate Player 1 ("X") pieces in bottom 3 rows (on dark squares: r+c is odd)
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 != 0:
                    self.grid[r][c] = "X"
                    
        self.current_turn = "X"
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "current_turn": self.current_turn
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.grid = copy.deepcopy(state.get("grid", [["" for _ in range(8)] for _ in range(8)]))
        self.current_turn = state.get("current_turn", "X")
        
    def get_valid_moves(self, player: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        if player != self.current_turn:
            return []
            
        jumps = []
        slides = []
        
        # Check all cells
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece.startswith(player):
                    piece_jumps, piece_slides = self._get_piece_moves(r, c, player, piece == f"{player}K")
                    jumps.extend(piece_jumps)
                    slides.extend(piece_slides)
                    
        # Force jump rule: If any jumps are available, the player MUST jump
        return jumps if jumps else slides
        
    def make_move(self, player: str, move: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
        valid_moves = self.get_valid_moves(player)
        if move in valid_moves:
            (sr, sc), (dr, dc) = move
            piece = self.grid[sr][sc]
            
            # Place piece in destination
            self.grid[dr][dc] = piece
            self.grid[sr][sc] = ""
            
            # If it's a jump, remove the captured piece
            if abs(dr - sr) == 2:
                cr = (sr + dr) // 2
                cc = (sc + dc) // 2
                self.grid[cr][cc] = ""
                
            # Promote to King if piece reaches the far side
            if player == "X" and dr == 0:
                self.grid[dr][dc] = "XK"
            elif player == "O" and dr == 7:
                self.grid[dr][dc] = "OK"
                
            # Switch turn
            self.current_turn = "O" if player == "X" else "X"
            return True
        return False
        
    def check_winner(self) -> Optional[str]:
        # Count remaining pieces & moves
        x_count = sum(row.count("X") + row.count("XK") for row in self.grid)
        o_count = sum(row.count("O") + row.count("OK") for row in self.grid)
        
        if x_count == 0:
            return "O"
        if o_count == 0:
            return "X"
            
        # Check if current player has no moves
        if not self.get_valid_moves(self.current_turn):
            return "O" if self.current_turn == "X" else "X"
            
        return None

    def _get_piece_moves(self, r: int, c: int, player: str, is_king: bool) -> Tuple[List[Any], List[Any]]:
        jumps = []
        slides = []
        
        opponent = "O" if player == "X" else "X"
        # Determine allowed directions
        if is_king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            # Regular "X" goes up (negative row index), "O" goes down (positive row index)
            directions = [(-1, -1), (-1, 1)] if player == "X" else [(1, -1), (1, 1)]
            
        for dr, dc in directions:
            # Slides
            sr, sc = r + dr, c + dc
            if 0 <= sr < 8 and 0 <= sc < 8 and self.grid[sr][sc] == "":
                slides.append(((r, c), (sr, sc)))
                
            # Jumps
            jr, jc = r + 2 * dr, c + 2 * dc
            if 0 <= jr < 8 and 0 <= jc < 8 and self.grid[jr][jc] == "":
                mid_r, mid_c = r + dr, c + dc
                mid_piece = self.grid[mid_r][mid_c]
                if mid_piece != "" and mid_piece.startswith(opponent):
                    jumps.append(((r, c), (jr, jc)))
                    
        return jumps, slides

    def get_board_visual(self) -> List[List[str]]:
        return self.grid
