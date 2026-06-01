import copy
import random
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class AirHockeyBoard(BaseGameBoard):
    """
    Air Hockey Game Engine (Tactical Grid-Based).
    Grid: 7 Rows x 5 Columns.
    - Rows: 0 to 6. Row 0 is Player 2 side, Row 6 is Player 1 side.
    - Player 1 ('X') controls Mallet at Row 5.
    - Player 2 ('O') controls Mallet at Row 1.
    - Puck starts at Row 3 (center).
    - Goal positions: (0, 2) (P2 Goal), (6, 2) (P1 Goal).
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        self.grid = [["" for _ in range(5)] for _ in range(7)]
        
        # Initial positions
        self.mallets = {"X": [5, 2], "O": [1, 2]} # (r, c)
        self.puck = [3, 2] # (r, c)
        
        self.current_turn = "X"
        self.scores = {"X": 0, "O": 0}
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "mallets": copy.deepcopy(self.mallets),
            "puck": copy.deepcopy(self.puck),
            "current_turn": self.current_turn,
            "scores": copy.deepcopy(self.scores)
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.mallets = copy.deepcopy(state.get("mallets", {"X": [5, 2], "O": [1, 2]}))
        self.puck = copy.deepcopy(state.get("puck", [3, 2]))
        self.current_turn = state.get("current_turn", "X")
        self.scores = copy.deepcopy(state.get("scores", {"X": 0, "O": 0}))
        
    def get_valid_moves(self, player: str) -> List[Tuple[int, int]]:
        if player != self.current_turn:
            return []
        if self.check_winner() is not None:
            return []
            
        # A move consists of choosing the slide angle (straight, diagonal-left, diagonal-right)
        # represented as a direction vector for the puck shoot.
        # Player X shoots UP (negative row direction): (-1, 0), (-1, -1), (-1, 1)
        # Player O shoots DOWN (positive row direction): (1, 0), (1, -1), (1, 1)
        if player == "X":
            return [(-1, 0), (-1, -1), (-1, 1)]
        else:
            return [(1, 0), (1, -1), (1, 1)]
            
    def make_move(self, player: str, move: Tuple[int, int]) -> bool:
        valid = self.get_valid_moves(player)
        if move not in valid:
            return False
            
        dr, dc = move
        pr, pc = self.puck
        
        # Simulate puck sliding
        curr_r, curr_c = pr, pc
        bounces = 0
        
        # Puck slides up to 4 cells
        for _ in range(4):
            curr_r += dr
            curr_c += dc
            
            # Wall bounces on columns (0 or 4)
            if curr_c < 0:
                curr_c = abs(curr_c)
                dc = -dc
            elif curr_c > 4:
                curr_c = 4 - (curr_c - 4)
                dc = -dc
                
            # Check Goal
            if curr_r == 0 and curr_c == 2:
                # Goal for Player 1 (X)
                self.scores["X"] += 1
                self._reset_puck()
                self.current_turn = "O" if player == "X" else "X"
                return True
            elif curr_r == 6 and curr_c == 2:
                # Goal for Player 2 (O)
                self.scores["O"] += 1
                self._reset_puck()
                self.current_turn = "O" if player == "X" else "X"
                return True
                
            # Intercepted by mallet check
            opponent = "O" if player == "X" else "X"
            mr, mc = self.mallets[opponent]
            if curr_r == mr and curr_c == mc:
                # Intercepted! Puck bounces back
                dr = -dr
                curr_r += dr
                break
                
            # Out of bounds safety clamp
            if curr_r < 0 or curr_r > 6:
                break
                
        # Update puck position
        self.puck = [max(0, min(6, curr_r)), max(0, min(4, curr_c))]
        
        # Move opponent mallet slightly (AI/Pre-move prediction) to try blocking next turn
        self._move_mallets()
        
        self.current_turn = "O" if player == "X" else "X"
        return True
        
    def check_winner(self) -> Optional[str]:
        if self.scores["X"] >= 3:
            return "X"
        if self.scores["O"] >= 3:
            return "O"
        return None
        
    def _reset_puck(self):
        self.puck = [3, 2]
        
    def _move_mallets(self):
        # Mallets slide left/right towards the puck's column
        for key in ["X", "O"]:
            mr, mc = self.mallets[key]
            p_col = self.puck[1]
            if mc < p_col:
                self.mallets[key][1] = min(4, mc + 1)
            elif mc > p_col:
                self.mallets[key][1] = max(0, mc - 1)

    def get_board_visual(self) -> List[List[str]]:
        # Render mallets and puck on grid
        temp_grid = [["" for _ in range(5)] for _ in range(7)]
        temp_grid[self.mallets["O"][0]][self.mallets["O"][1]] = "O_MALLET"
        temp_grid[self.mallets["X"][0]][self.mallets["X"][1]] = "X_MALLET"
        temp_grid[self.puck[0]][self.puck[1]] = "PUCK"
        # Mark goals
        temp_grid[0][2] = "[GOAL]"
        temp_grid[6][2] = "[GOAL]"
        return temp_grid
