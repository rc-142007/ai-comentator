from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from typing import Optional

# Platform imports
from backend.room_manager import RoomManager
from commentator.rule_commentator import RuleBasedCommentator  # 🌟 Added import

app = FastAPI(title="RetroRadial Authority Board Game Server")

# Allow CORS for local and deployment domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

room_manager = RoomManager()
live_commentator = RuleBasedCommentator()  # 🌟 Instantiated commentator

class RoomCreatePayload(BaseModel):
    game_id: str

@app.post("/api/rooms/create")
def create_room(payload: RoomCreatePayload):
    try:
        room_code = room_manager.create_room(payload.game_id)
        return {"room_code": room_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/{room_code}/status")
def get_room_status(room_code: str):
    room = room_manager.get_room(room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {
        "room_code": room.room_id,
        "game_id": room.game_id,
        "players": list(room.player_symbols.keys()),
        "symbols": room.player_symbols,
        "current_turn": room.game.current_turn
    }

@app.websocket("/ws/{room_code}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, player_id: str):
    await websocket.accept()
    room = room_manager.get_room(room_code)
    if not room:
        await websocket.close(code=4004)
        return
        
    symbol = room.add_player(player_id, websocket)
    
    # Broadcast joiner info
    join_payload = json.dumps({
        "type": "player_joined",
        "player_id": player_id,
        "symbol": symbol,
        "board_state": room.game.get_state(),
        "winner": room.game.check_winner(),
        "current_turn": room.game.current_turn
    })
    for p_id, client_ws in room.clients.items():
        await client_ws.send_text(join_payload)
        
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "move":
                move_val = message.get("move")
                # Parse move if sent as string list (e.g. coordinates or points)
                if isinstance(move_val, list):
                    move_val = tuple(move_val)
                    if len(move_val) == 2 and isinstance(move_val[0], list):
                        # Nested coordinates: slide moves e.g., ((r,c), (r,c))
                        move_val = (tuple(move_val[0]), tuple(move_val[1]))
                
                # Make authoritative move validation
                if room.game.make_move(symbol, move_val):
                    winner = room.game.check_winner()
                    
                    # 🌟 Generate the custom rule-based commentary dictionary dynamically!
                    commentary_payload = live_commentator.generate_commentary(room.game, move_val, symbol)
                    
                    update_payload = json.dumps({
                        "type": "update",
                        "board_state": room.game.get_state(),
                        "winner": winner,
                        "current_turn": room.game.current_turn,
                        "last_move": move_val,
                        "last_player": symbol,
                        "commentary": commentary_payload  # 🚀 Broadcast it out live over the server pipes!
                    })
                    for client_ws in room.clients.values():
                        await client_ws.send_text(update_payload)
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid Move!"
                    }))
                    
            elif message.get("type") == "reset":
                room.game.reset()
                reset_payload = json.dumps({
                    "type": "reset",
                    "board_state": room.game.get_state(),
                    "current_turn": room.game.current_turn
                })
                for client_ws in room.clients.values():
                    await client_ws.send_text(reset_payload)
                    
    except WebSocketDisconnect:
        room.remove_player(player_id)
        # Broadcast disconnect
        disconnect_payload = json.dumps({
            "type": "player_left",
            "player_id": player_id
        })
        for client_ws in room.clients.values():
            try:
                await client_ws.send_text(disconnect_payload)
            except:
                pass
                
        # Clean up room if empty
        if len(room.clients) == 0:
            room_manager.close_room(room_code)