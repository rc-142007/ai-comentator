import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import webbrowser
import os

# Core Platform Engine Imports
from games.game_registry import GAME_METADATA, get_game_instance
from bot.random_bot import RandomBot
from commentator.rule_commentator import RuleBasedCommentator
from backend.database import GameDatabase

# Initialize authoritative platform modules
db = GameDatabase()
bot = RandomBot()
commentator = RuleBasedCommentator()

# Central Shared Runtime State Matrix
GLOBAL_STATE = {
    "active_game_id": None,
    "game_board": None,
    "username": "Challenger",
    "bot_difficulty": "easy",
    "commentary_text": "Arena stabilized. Select a battleground card below to begin.",
    "avatar_reaction": "🤖",
    "winner": None,
    "grid": []
}

class GameBridgeRequestHandler(BaseHTTPRequestHandler):
    """
    Unified HTTP Server Handler. 
    Serves the index.html frontend file directly over HTTP to bypass all browser 
    CORS security rules and acts as a REST API gateway for the game engines.
    """
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # 1. Base UI File Delivery Route
        if self.path == "/" or self.path == "/index.html":
            script_dir = os.path.dirname(os.path.abspath(__file__))
            html_file_path = os.path.join(script_dir, "index.html")
            
            if not os.path.exists(html_file_path):
                html_file_path = "index.html"
                
            if not os.path.exists(html_file_path):
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                error_html = f"""
                <html>
                <body style="background:#090615; color:#f3f4f6; font-family:sans-serif; text-align:center; padding-top:100px;">
                    <h1 style="color:#ef4444;">⚠️ index.html File Missing!</h1>
                    <p>Python is running, but it cannot find your <b>index.html</b> file.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode("utf-8"))
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            with open(html_file_path, "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode("utf-8"))
            return

        # Handle data endpoints safely
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        if self.path == "/api/launcher/init":
            stats = db.get_stats()
            init_payload = {
                "username": GLOBAL_STATE["username"],
                "elo": db.get_user_elo(GLOBAL_STATE["username"]),
                "total_matches": stats["total_matches"],
                "human_wins": stats["human_wins"],
                "games_metadata": GAME_METADATA
            }
            self.wfile.write(json.dumps(init_payload).encode("utf-8"))
            
        elif self.path == "/api/arena/state":
            state_payload = {
                "game_id": GLOBAL_STATE["active_game_id"],
                "grid": GLOBAL_STATE["grid"],
                "turn": GLOBAL_STATE["game_board"].current_turn if GLOBAL_STATE["game_board"] else "",
                "winner": GLOBAL_STATE["winner"],
                "commentary": GLOBAL_STATE["commentary_text"],
                "avatar": GLOBAL_STATE["avatar_reaction"]
            }
            self.wfile.write(json.dumps(state_payload).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        payload = json.loads(post_data.decode('utf-8'))

        # 🌟 FIX: Ensure EVERY single response stream path explicitly opens and closes headers cleanly to avoid client-side hangs
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if self.path == "/api/arena/start":
            game_key = payload.get("game_id", "").lower()
            GLOBAL_STATE["active_game_id"] = game_key
            GLOBAL_STATE["game_board"] = get_game_instance(game_key)
            
            GLOBAL_STATE["grid"] = GLOBAL_STATE["game_board"].get_board_visual()
            GLOBAL_STATE["winner"] = None
            GLOBAL_STATE["commentary_text"] = f"Began a fresh {GAME_METADATA[game_key]['name']} match. Make your move!"
            GLOBAL_STATE["avatar_reaction"] = "🔥"
            
            self.wfile.write(json.dumps({"status": "success", "game_id": game_key}).encode("utf-8"))

        elif self.path == "/api/arena/move":
            move_val = payload.get("move")
            game = GLOBAL_STATE["game_board"]
            
            if game and not GLOBAL_STATE["winner"]:
                if isinstance(move_val, list):
                    if len(move_val) == 2 and isinstance(move_val[0], list):
                        move_val = (tuple(move_val[0]), tuple(move_val[1]))
                    else:
                        move_val = tuple(move_val)
                
                current_player = game.current_turn
                
                if game.make_move(current_player, move_val):
                    GLOBAL_STATE["grid"] = game.get_board_visual()
                    GLOBAL_STATE["winner"] = game.check_winner()
                    
                    comm = commentator.generate_commentary(game, move_val, current_player)
                    GLOBAL_STATE["commentary_text"] = comm["text"]
                    GLOBAL_STATE["avatar_reaction"] = comm["avatar_reaction"]
                    
                    if not GLOBAL_STATE["winner"] and game.current_turn in ["O", "B"]:
                        time.sleep(0.1)
                        bot_player = game.current_turn
                        bot_move = bot.select_move(game, bot_player, GLOBAL_STATE["bot_difficulty"])
                        if bot_move is not None:
                            game.make_move(bot_player, bot_move)
                            GLOBAL_STATE["grid"] = game.get_board_visual()
                            GLOBAL_STATE["winner"] = game.check_winner()
                            
                            bot_comm = commentator.generate_commentary(game, bot_move, bot_player)
                            GLOBAL_STATE["commentary_text"] = bot_comm["text"]
                            GLOBAL_STATE["avatar_reaction"] = bot_comm["avatar_reaction"]

                    if GLOBAL_STATE["winner"]:
                        db.record_match("match_" + str(int(time.time())), GLOBAL_STATE["active_game_id"], "Human", "Bot", GLOBAL_STATE["winner"], 10, 60)
            
            self.wfile.write(json.dumps({"status": "processed"}).encode("utf-8"))

        elif self.path == "/api/arena/exit":
            # 🌟 CLEAN RESET MATRIX STATE PIPELINE
            GLOBAL_STATE["active_game_id"] = None
            GLOBAL_STATE["game_board"] = None
            GLOBAL_STATE["grid"] = []
            GLOBAL_STATE["winner"] = None
            GLOBAL_STATE["avatar_reaction"] = "🤖"
            GLOBAL_STATE["commentary_text"] = "Lobby reset completed cleanly."
            
            self.wfile.write(json.dumps({"status": "exited"}).encode("utf-8"))

def run_backend_server():
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, GameBridgeRequestHandler)
    print("🚀 [SERVER ONLINE] Listening smoothly at http://localhost:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_backend_server, daemon=True).start()
    time.sleep(1)
    webbrowser.open("http://localhost:8000")
    while True:
        time.sleep(1)