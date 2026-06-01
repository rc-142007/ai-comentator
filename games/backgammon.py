import copy
import random
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class BackgammonBoard(BaseGameBoard):
    """
    Backgammon Board Game Engine (Simplified Turn-Based).
    Points: 24 points indexed 0 to 23.
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        # Each point is represented by [owner, count]. Owner: "X", "O", or ""
        self.points = [["", 0] for _ in range(24)]
        
        # Standard starting position
        self.points[0]  = ["X", 2]
        self.points[5]  = ["O", 5]
        self.points[7]  = ["O", 3]
        self.points[11] = ["X", 5]
        self.points[12] = ["O", 5]
        self.points[16] = ["X", 3]
        self.points[18] = ["X", 5]
        self.points[23] = ["O", 2]
        
        self.current_turn = "X"
        self.bar = {"X": 0, "O": 0}
        self.off = {"X": 0, "O": 0}
        self.dice = [random.randint(1, 6), random.randint(1, 6)]
        self.moves_left = 2 # Normal roll has 2 moves; doubles get 4 (simplified to 2 for ease of play)
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "points": copy.deepcopy(self.points),
            "current_turn": self.current_turn,
            "bar": copy.deepcopy(self.bar),
            "off": copy.deepcopy(self.off),
            "dice": copy.deepcopy(self.dice),
            "moves_left": self.moves_left
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.points = copy.deepcopy(state.get("points", []))
        self.current_turn = state.get("current_turn", "X")
        self.bar = copy.deepcopy(state.get("bar", {"X": 0, "O": 0}))
        self.off = copy.deepcopy(state.get("off", {"X": 0, "O": 0}))
        self.dice = copy.deepcopy(state.get("dice", [1, 1]))
        self.moves_left = state.get("moves_left", 2)
        
    def roll_dice(self) -> List[int]:
        self.dice = [random.randint(1, 6), random.randint(1, 6)]
        self.moves_left = 4 if self.dice[0] == self.dice[1] else 2
        return self.dice
        
    def get_valid_moves(self, player: str) -> List[Tuple[int, int]]:
        if player != self.current_turn:
            return []
        if self.moves_left <= 0:
            return []
            
        valid = []
        # Directions: X moves 0 -> 23 (forward), O moves 23 -> 0 (backward)
        step_dir = 1 if player == "X" else -1
        
        # If there are checkers on the bar, the player MUST move them first
        if self.bar[player] > 0:
            start_idx = -1 if player == "X" else 24
            for die in self.dice:
                dest = start_idx + step_dir * die
                if self._can_land_on(dest, player):
                    valid.append(("bar", dest))
            return valid
            
        # Normal moves from points
        for i in range(24):
            owner, count = self.points[i]
            if owner == player and count > 0:
                for die in self.dice:
                    dest = i + step_dir * die
                    # Bearing off check
                    if player == "X" and dest >= 24:
                        if self._can_bear_off(player):
                            valid.append((i, "off"))
                    elif player == "O" and dest < 0:
                        if self._can_bear_off(player):
                            valid.append((i, "off"))
                    elif 0 <= dest < 24:
                        if self._can_land_on(dest, player):
                            valid.append((i, dest))
        return valid
        
    def make_move(self, player: str, move: Tuple[Any, Any]) -> bool:
        valid = self.get_valid_moves(player)
        if move not in valid:
            return False
            
        start, dest = move
        opponent = "O" if player == "X" else "X"
        
        # 1. Deduct checker from starting point/bar
        if start == "bar":
            self.bar[player] -= 1
        else:
            self.points[start][1] -= 1
            if self.points[start][1] == 0:
                self.points[start][0] = ""
                
        # 2. Add checker to destination point/off
        if dest == "off":
            self.off[player] += 1
        else:
            dest_owner, dest_count = self.points[dest]
            # Capture blot
            if dest_owner == opponent and dest_count == 1:
                self.bar[opponent] += 1
                self.points[dest] = [player, 1]
            else:
                self.points[dest] = [player, dest_count + 1]
                
        self.moves_left -= 1
        if self.moves_left <= 0:
            # End turn, switch player, and auto-roll next dice
            self.current_turn = opponent
            self.roll_dice()
            
        return True
        
    def check_winner(self) -> Optional[str]:
        if self.off["X"] == 15:
            return "X"
        if self.off["O"] == 15:
            return "O"
        return None
        
    def _can_land_on(self, point_idx: int, player: str) -> bool:
        opponent = "O" if player == "X" else "X"
        owner, count = self.points[point_idx]
        # Empty, owned by player, or blotted by opponent (count is 1)
        return owner == "" or owner == player or (owner == opponent and count == 1)
        
    def _can_bear_off(self, player: str) -> bool:
        # A player can only bear off if all 15 checkers are in their home board
        # Player X home board: points 18 to 23
        # Player O home board: points 0 to 5
        home_range = range(18, 24) if player == "X" else range(0, 6)
        checkers_in_home = sum(count for i, (owner, count) in enumerate(self.points) if owner == player and i in home_range)
        return (checkers_in_home + self.off[player] + self.bar[player]) == 15

    def get_board_visual(self) -> List[List[Any]]:
        return self.points
