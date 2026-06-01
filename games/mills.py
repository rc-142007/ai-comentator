import copy
from typing import Dict, Any, List, Optional, Tuple
from games.base import BaseGameBoard

class MillsBoard(BaseGameBoard):
    """
    Mills (Nine Men's Morris) Board Game Engine.
    Intersections: 24 nodes numbered 0 to 23.
    """
    def __init__(self):
        self.reset()
        
    def reset(self) -> None:
        # 24 nodes: "" for empty, "X" or "O"
        self.nodes = [""] * 24
        self.current_turn = "X"
        self.pieces_to_place = {"X": 9, "O": 9}
        self.mill_formed_awaiting_removal = False
        
        # Define adjacencies
        self.adjacencies = {
            0: [1, 9], 1: [0, 2, 4], 2: [1, 14],
            3: [4, 10], 4: [3, 5, 1, 7], 5: [4, 13],
            6: [7, 11], 7: [6, 8, 4], 8: [7, 12],
            9: [0, 10, 21], 10: [9, 3, 11, 18], 11: [10, 6, 15],
            12: [8, 13, 17], 13: [12, 5, 14, 20], 14: [13, 2, 23],
            15: [11, 16], 16: [15, 17, 19], 17: [16, 12],
            18: [10, 19], 19: [18, 20, 16, 22], 20: [19, 13],
            21: [9, 22], 22: [21, 23, 19], 23: [22, 14]
        }
        
        # Define mills combinations
        self.mills_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [9, 10, 11], [12, 13, 14], [15, 16, 17],
            [18, 19, 20], [21, 22, 23],
            [0, 9, 21], [3, 10, 18], [6, 11, 15],
            [1, 4, 7], [16, 19, 22],
            [8, 12, 17], [5, 13, 20], [2, 14, 23]
        ]
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "nodes": copy.deepcopy(self.nodes),
            "current_turn": self.current_turn,
            "pieces_to_place": copy.deepcopy(self.pieces_to_place),
            "mill_formed_awaiting_removal": self.mill_formed_awaiting_removal
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        self.nodes = copy.deepcopy(state.get("nodes", [""] * 24))
        self.current_turn = state.get("current_turn", "X")
        self.pieces_to_place = copy.deepcopy(state.get("pieces_to_place", {"X": 9, "O": 9}))
        self.mill_formed_awaiting_removal = state.get("mill_formed_awaiting_removal", False)
        
    def get_valid_moves(self, player: str) -> List[Any]:
        if player != self.current_turn:
            return []
            
        # Removal phase
        if self.mill_formed_awaiting_removal:
            opponent = "O" if player == "X" else "X"
            # Can remove any opponent piece that is not part of a mill, unless all opponent pieces are in mills
            opponent_nodes = [i for i, node in enumerate(self.nodes) if node == opponent]
            non_mill_opponent_nodes = [i for i in opponent_nodes if not self._is_in_mill(i, opponent)]
            return non_mill_opponent_nodes if non_mill_opponent_nodes else opponent_nodes
            
        # Placement phase
        if self.pieces_to_place[player] > 0:
            return [i for i, val in enumerate(self.nodes) if val == ""]
            
        # Movement phase
        valid = []
        player_nodes = [i for i, val in enumerate(self.nodes) if val == player]
        
        # Flying rule: If a player only has 3 pieces, they can fly/jump to any empty node
        if len(player_nodes) == 3:
            empty_nodes = [i for i, val in enumerate(self.nodes) if val == ""]
            for start in player_nodes:
                for dest in empty_nodes:
                    valid.append((start, dest))
        else:
            for start in player_nodes:
                for neighbor in self.adjacencies[start]:
                    if self.nodes[neighbor] == "":
                        valid.append((start, neighbor))
        return valid
        
    def make_move(self, player: str, move: Any) -> bool:
        valid_moves = self.get_valid_moves(player)
        if move not in valid_moves:
            return False
            
        # 1. Removal
        if self.mill_formed_awaiting_removal:
            self.nodes[move] = ""
            self.mill_formed_awaiting_removal = False
            self.current_turn = "O" if player == "X" else "X"
            return True
            
        # 2. Placement
        if self.pieces_to_place[player] > 0:
            self.nodes[move] = player
            self.pieces_to_place[player] -= 1
            
            # Check if this placement formed a mill
            if self._is_in_mill(move, player):
                self.mill_formed_awaiting_removal = True
                # Turn stays same to allow removal
            else:
                self.current_turn = "O" if player == "X" else "X"
            return True
            
        # 3. Movement
        start, dest = move
        self.nodes[start] = ""
        self.nodes[dest] = player
        
        # Check if movement formed a mill
        if self._is_in_mill(dest, player):
            self.mill_formed_awaiting_removal = True
        else:
            self.current_turn = "O" if player == "X" else "X"
        return True
        
    def check_winner(self) -> Optional[str]:
        # Only checks winner after all pieces are placed
        if self.pieces_to_place["X"] > 0 or self.pieces_to_place["O"] > 0:
            return None
            
        x_count = self.nodes.count("X")
        o_count = self.nodes.count("O")
        
        if x_count < 3:
            return "O"
        if o_count < 3:
            return "X"
            
        # Check stalemate (no moves)
        if not self.get_valid_moves(self.current_turn):
            return "O" if self.current_turn == "X" else "X"
            
        return None
        
    def _is_in_mill(self, node: int, player: str) -> bool:
        # Check if the node is part of any three-in-a-row mill combo
        for combo in self.mills_combos:
            if node in combo:
                if self.nodes[combo[0]] == self.nodes[combo[1]] == self.nodes[combo[2]] == player:
                    return True
        return False

    def get_board_visual(self) -> List[str]:
        return self.nodes
