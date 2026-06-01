import random
from typing import Dict, Any
from commentator.base_commentator import BaseAICommentator
from games.base import BaseGameBoard

class RuleBasedCommentator(BaseAICommentator):
    """
    A smart, rule-based AI commentator that evaluates the game state and generates
    context-aware, highly witty commentary with fitting avatars and reactions.
    """
    
    def generate_commentary(self, game: BaseGameBoard, last_move: Any, last_player: str) -> Dict[str, Any]:
        game_name = game.__class__.__name__.replace("Board", "").replace("Game", "").lower()
        winner = game.check_winner()
        
        # 1. Victory / Game Over reactions
        if winner:
            if winner == "draw":
                return {
                    "text": "An absolute clash of titans ends in a stalemate! Mutual respect all around.",
                    "sentiment": "analytical",
                    "avatar_reaction": "🤝"
                }
            else:
                return {
                    "text": f"SPECTACULAR! Player {winner} has claimed a glorious victory! What a masterclass performance!",
                    "sentiment": "excited",
                    "avatar_reaction": "🏆"
                }
                
        # 2. Game-Specific reactions
        if game_name == "tictactoe":
            return self._tictactoe_commentary(game, last_move, last_player)
        elif game_name == "connectfour":
            return self._connectfour_commentary(game, last_move, last_player)
        elif game_name == "reversi":
            return self._reversi_commentary(game, last_move, last_player)
        elif game_name == "mancala":
            return self._mancala_commentary(game, last_move, last_player)
            
        # 3. Generic fallback reactions
        generic_phrases = [
            f"Player {last_player} plays a strategic move. The tension is palpable!",
            f"An interesting placement. What is Player {last_player} cooking?",
            f"A solid defensive move. Keeping the position closed and safe.",
            "They are pushing the tempo! A fascinating tactical sequence unfolds.",
            "A masterfully calculated move. The board state shifts dynamically!"
        ]
        
        return {
            "text": random.choice(generic_phrases),
            "sentiment": "analytical",
            "avatar_reaction": random.choice(["🤔", "🔥", "⚡", "👀"])
        }

    def _tictactoe_commentary(self, game: BaseGameBoard, last_move: Any, last_player: str) -> Dict[str, Any]:
        grid = game.get_board_visual()
        # Center square move
        if last_move == 4:
            return {
                "text": f"Ah, the classic center claim! Player {last_player} takes control of the heart of the grid.",
                "sentiment": "analytical",
                "avatar_reaction": "🎯"
            }
        # Corners
        elif last_move in [0, 2, 6, 8]:
            return {
                "text": f"Claiming a strategic corner! Player {last_player} is aiming for a dual-threat setup.",
                "sentiment": "excited",
                "avatar_reaction": "📐"
            }
        else:
            return {
                "text": f"Filling the side. A solid blocking move to neutralize threats.",
                "sentiment": "analytical",
                "avatar_reaction": "🛡️"
            }

    def _connectfour_commentary(self, game: BaseGameBoard, last_move: Any, last_player: str) -> Dict[str, Any]:
        # last_move is the column index (0-6)
        if last_move == 3:
            return {
                "text": f"Player {last_player} claims the center column! The battle for vertical dominance is on.",
                "sentiment": "analytical",
                "avatar_reaction": "🔥"
            }
        return {
            "text": f"Dropping a disc in column {last_move + 1}. Building stack pressure!",
            "sentiment": "analytical",
            "avatar_reaction": "👀"
        }

    def _reversi_commentary(self, game: BaseGameBoard, last_move: Any, last_player: str) -> Dict[str, Any]:
        # last_move is (row, col)
        r, c = last_move
        # Corners are high value in Reversi
        if (r == 0 or r == 7) and (c == 0 or c == 7):
            return {
                "text": f"INCREDIBLE! Player {last_player} captures a corner! A massive strategic advantage!",
                "sentiment": "excited",
                "avatar_reaction": "🤯"
            }
        return {
            "text": f"Pieces flipped! Player {last_player} expands their territory in the center board.",
            "sentiment": "analytical",
            "avatar_reaction": "🔄"
        }

    def _mancala_commentary(self, game: BaseGameBoard, last_move: Any, last_player: str) -> Dict[str, Any]:
        return {
            "text": f"Sowing seeds from pit {last_move + 1}. A beautiful mathematical flow of pebbles!",
            "sentiment": "analytical",
            "avatar_reaction": "💎"
        }
