import copy
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class ChessGameBoard(BaseGameBoard):
    """
    Pure Python Chess Game Engine.
    Pieces representation:
    - White: 'WP' (Pawn), 'WR' (Rook), 'WN' (Knight), 'WB' (Bishop), 'WQ' (Queen), 'WK' (King)
    - Black: 'BP' (Pawn), 'BR' (Rook), 'BN' (Knight), 'BB' (Bishop), 'BQ' (Queen), 'BK' (King)
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        self.grid = [
            ["BR", "BN", "BB", "BQ", "BK", "BB", "BN", "BR"],
            ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
            ["WR", "WN", "WB", "WQ", "WK", "WB", "WN", "WR"]
        ]
        self.current_turn = "W" # W for White, B for Black
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "grid": copy.deepcopy(self.grid),
            "current_turn": self.current_turn
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.grid = copy.deepcopy(state.get("grid", []))
        self.current_turn = state.get("current_turn", "W")
        
    def get_valid_moves(self, player: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        if player != self.current_turn:
            return []
            
        valid = []
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece != "" and piece.startswith(player):
                    for tr in range(8):
                        for tc in range(8):
                            if self._is_valid_piece_move((r, c), (tr, tc), piece):
                                valid.append(((r, c), (tr, tc)))
        return valid
        
    def make_move(self, player: str, move: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
        valid = self.get_valid_moves(player)
        if move in valid:
            (sr, sc), (dr, dc) = move
            piece = self.grid[sr][sc]
            self.grid[dr][dc] = piece
            self.grid[sr][sc] = ""
            
            # Switch turn
            self.current_turn = "B" if player == "W" else "W"
            return True
        return False
        
    def check_winner(self) -> Optional[str]:
        # Check if King is missing
        w_king_alive = any("WK" in row for row in self.grid)
        b_king_alive = any("BK" in row for row in self.grid)
        
        if not w_king_alive:
            return "B"
        if not b_king_alive:
            return "W"
        return None

    def _is_valid_piece_move(self, start: Tuple[int, int], dest: Tuple[int, int], piece: str) -> bool:
        sr, sc = start
        dr, dc = dest
        if sr == dr and sc == dc:
            return False
            
        dest_piece = self.grid[dr][dc]
        # Can't capture own pieces
        if dest_piece != "" and dest_piece.startswith(piece[0]):
            return False
            
        piece_type = piece[1]
        color = piece[0]
        
        # 1. Pawn
        if piece_type == "P":
            direction = -1 if color == "W" else 1
            # Standard single move forward
            if dr == sr + direction and dc == sc:
                return dest_piece == ""
            # Double move from initial rank
            if color == "W" and sr == 6 and dr == 4 and dc == sc:
                return self.grid[5][sc] == "" and dest_piece == ""
            if color == "B" and sr == 1 and dr == 3 and dc == sc:
                return self.grid[2][sc] == "" and dest_piece == ""
            # Diagonal capture
            if dr == sr + direction and abs(dc - sc) == 1:
                return dest_piece != "" and not dest_piece.startswith(color)
                
        # 2. Rook
        elif piece_type == "R":
            if sr == dr or sc == dc:
                return self._is_path_clear(start, dest)
                
        # 3. Bishop
        elif piece_type == "B":
            if abs(dr - sr) == abs(dc - sc):
                return self._is_path_clear(start, dest)
                
        # 4. Knight
        elif piece_type == "N":
            return (abs(dr - sr), abs(dc - sc)) in [(1, 2), (2, 1)]
            
        # 5. Queen
        elif piece_type == "Q":
            if sr == dr or sc == dc or abs(dr - sr) == abs(dc - sc):
                return self._is_path_clear(start, dest)
                
        # 6. King
        elif piece_type == "K":
            return abs(dr - sr) <= 1 and abs(dc - sc) <= 1
            
        return False
        
    def _is_path_clear(self, start: Tuple[int, int], dest: Tuple[int, int]) -> bool:
        sr, sc = start
        dr, dc = dest
        
        row_step = 0 if sr == dr else (1 if dr > sr else -1)
        col_step = 0 if sc == dc else (1 if dc > sc else -1)
        
        curr_r, curr_c = sr + row_step, sc + col_step
        while curr_r != dr or curr_c != dc:
            if self.grid[curr_r][curr_c] != "":
                return False
            curr_r += row_step
            curr_c += col_step
            
        return True

    def get_board_visual(self) -> List[List[str]]:
        return self.grid
