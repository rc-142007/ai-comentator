from typing import Dict, Type
from games.base import BaseGameBoard
from games.tictactoe import TicTacToeBoard
from games.connect_four import ConnectFourBoard
from games.reversi import ReversiBoard
from games.mancala import MancalaBoard
from games.checkers import CheckersBoard
from games.hex import HexBoard
from games.chess_game import ChessGameBoard
from games.go import GoBoard
from games.mills import MillsBoard
from games.tiger_chess import TigerChessBoard
from games.backgammon import BackgammonBoard
from games.carrom import CarromBoard
from games.air_hockey import AirHockeyBoard

# Registry of all available games on the platform
GAME_REGISTRY: Dict[str, Type[BaseGameBoard]] = {
    "tictactoe": TicTacToeBoard,
    "connectfour": ConnectFourBoard,
    "reversi": ReversiBoard,
    "mancala": MancalaBoard,
    "checkers": CheckersBoard,
    "hex": HexBoard,
    "chess": ChessGameBoard,
    "go": GoBoard,
    "mills": MillsBoard,
    "tigerchess": TigerChessBoard,
    "backgammon": BackgammonBoard,
    "carrom": CarromBoard,
    "airhockey": AirHockeyBoard
}

GAME_METADATA = {
    "tictactoe": {"name": "Tic-Tac-Toe", "emoji": "⭕", "players": "2 (X/O)", "difficulty": "Easy"},
    "connectfour": {"name": "Connect Four", "emoji": "🟡", "players": "2 (Y/R)", "difficulty": "Medium"},
    "reversi": {"name": "Reversi", "emoji": "⚪", "players": "2 (B/W)", "difficulty": "Hard"},
    "mancala": {"name": "Mancala", "emoji": "💎", "players": "2", "difficulty": "Medium"},
    "checkers": {"name": "Checkers", "emoji": "🔴", "players": "2", "difficulty": "Medium"},
    "hex": {"name": "Hex", "emoji": "⬡", "players": "2", "difficulty": "Hard"},
    "chess": {"name": "Chess", "emoji": "♔", "players": "2", "difficulty": "Very Hard"},
    "go": {"name": "Go (Weiqi)", "emoji": "⚫", "players": "2", "difficulty": "Extreme"},
    "mills": {"name": "Mills (Morris)", "emoji": "⚔", "players": "2", "difficulty": "Hard"},
    "tigerchess": {"name": "Tiger Chess", "emoji": "🐯", "players": "2 (Asymmetric)", "difficulty": "Hard"},
    "backgammon": {"name": "Backgammon", "emoji": "🎲", "players": "2", "difficulty": "Medium"},
    "carrom": {"name": "Carrom Board", "emoji": "🎯", "players": "2", "difficulty": "Medium"},
    "airhockey": {"name": "Air Hockey", "emoji": "🏒", "players": "2", "difficulty": "Easy"}
}

def get_game_instance(game_id: str) -> BaseGameBoard:
    """Instantiates a game engine by its registered ID."""
    if game_id not in GAME_REGISTRY:
        raise ValueError(f"Game '{game_id}' is not registered.")
    return GAME_REGISTRY[game_id]()
