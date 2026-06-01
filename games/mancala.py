import copy
from typing import Dict, Any, List, Optional
from games.base import BaseGameBoard

class MancalaBoard(BaseGameBoard):
    """
    Mancala (Kalah) Board Game Engine.
    Indices:
    - 0 to 5: Player 1 pits (left to right)
    - 6: Player 1 store
    - 7 to 12: Player 2 pits (right to left / opposite row)
    - 13: Player 2 store
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        # Standard Kalah starts with 4 seeds in each of the 12 pits, and 0 in stores.
        self.board = [4] * 6 + [0] + [4] * 6 + [0]
        self.current_turn = "X" # X is Player 1, O is Player 2
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "board": copy.deepcopy(self.board),
            "current_turn": self.current_turn
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.board = copy.deepcopy(state.get("board", [4] * 6 + [0] + [4] * 6 + [0]))
        self.current_turn = state.get("current_turn", "X")
        
    def get_valid_moves(self, player: str) -> List[int]:
        if player != self.current_turn:
            return []
        if self.check_winner() is not None:
            return []
            
        if player == "X":
            # Player X can pick indices 0 to 5, as long as they contain seeds
            return [i for i in range(6) if self.board[i] > 0]
        else:
            # Player O can pick indices 7 to 12, as long as they contain seeds
            return [i for i in range(7, 13) if self.board[i] > 0]
            
    def make_move(self, player: str, move: int) -> bool:
        if move not in self.get_valid_moves(player):
            return False
            
        seeds = self.board[move]
        self.board[move] = 0
        
        curr_idx = move
        while seeds > 0:
            curr_idx = (curr_idx + 1) % 14
            
            # Skip opponent's store
            if player == "X" and curr_idx == 13:
                continue
            if player == "O" and curr_idx == 6:
                continue
                
            self.board[curr_idx] += 1
            seeds -= 1
            
        # Capture rule: If the last seed lands in an empty pit on the player's side,
        # they capture all seeds in the opposite pit plus their landing seed.
        if player == "X" and 0 <= curr_idx <= 5 and self.board[curr_idx] == 1:
            opposite_idx = 12 - curr_idx
            if self.board[opposite_idx] > 0:
                self.board[6] += self.board[opposite_idx] + 1
                self.board[opposite_idx] = 0
                self.board[curr_idx] = 0
                
        elif player == "O" and 7 <= curr_idx <= 12 and self.board[curr_idx] == 1:
            opposite_idx = 12 - curr_idx # opposite of 7 is 5, opposite of 12 is 0
            if self.board[opposite_idx] > 0:
                self.board[13] += self.board[opposite_idx] + 1
                self.board[opposite_idx] = 0
                self.board[curr_idx] = 0
                
        # Extra turn rule: If the last seed lands in the player's own store, they get another turn.
        if player == "X" and curr_idx == 6:
            # Extra turn for X, do not change current_turn
            pass
        elif player == "O" and curr_idx == 13:
            # Extra turn for O, do not change current_turn
            pass
        else:
            # Swap turns
            self.current_turn = "O" if player == "X" else "X"
            
        # Check if either side is empty; if so, collect remaining seeds to their respective stores
        self._check_and_resolve_game_end()
        return True
        
    def _check_and_resolve_game_end(self):
        x_empty = all(self.board[i] == 0 for i in range(6))
        o_empty = all(self.board[i] == 0 for i in range(7, 13))
        
        if x_empty or o_empty:
            # Sweep remaining seeds to the respective stores
            for i in range(6):
                self.board[6] += self.board[i]
                self.board[i] = 0
            for i in range(7, 13):
                self.board[13] += self.board[i]
                self.board[i] = 0
                
    def check_winner(self) -> Optional[str]:
        # Game ends when either player has no valid moves left (which is checked via board sweep)
        x_has_moves = any(self.board[i] > 0 for i in range(6))
        o_has_moves = any(self.board[i] > 0 for i in range(7, 13))
        
        if x_has_moves and o_has_moves:
            return None
            
        # Game over, compare store counts
        x_score = self.board[6]
        o_score = self.board[13]
        
        if x_score > o_score:
            return "X"
        elif o_score > x_score:
            return "O"
        else:
            return "draw"
            
    def get_board_visual(self) -> List[int]:
        return self.board
