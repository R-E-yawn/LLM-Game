"""
Main FastAPI Application
Among Us-style deduction game with LLM-powered players
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
import os

from app.database import get_db, init_db
from app.models import GameSession, ChatMessage
from app.game_state import (
    create_game_session,
    get_game_session,
    add_chat_message,
    get_chat_messages,
)
from app.llm_service import OpenAIService
from app.event_generator import generate_game_data, PLAYER_COLORS, COLOR_TO_PLAYER
from app.guardrails import apply_output_guardrail

app = FastAPI(title="Impostor.AI Game API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# In-memory storage for game state (in production, use database)
game_states = {}

# Request/Response models
class InitGameRequest(BaseModel):
    api_key: str

class InitGameResponse(BaseModel):
    success: bool
    message: str
    game_id: Optional[str] = None
    impostor_color: Optional[str] = None

class PlayerChatRequest(BaseModel):
    game_id: str
    color: str
    message: str

class PlayerChatResponse(BaseModel):
    response: str
    color: str


# API Routes

@app.post("/api/game/init", response_model=InitGameResponse)
async def init_game(request: InitGameRequest, db: Session = Depends(get_db)):
    """Initialize a new game - generates events and assigns impostor"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=request.api_key)
        
        # Quick validation
        try:
            client.models.list()
        except Exception as e:
            return InitGameResponse(
                success=False,
                message=f"Invalid API key: {str(e)}"
            )
        
        # Generate game data
        print("[INIT_GAME] Generating game data...")
        game_data = generate_game_data(request.api_key, num_periods=10)
        
        import uuid
        game_id = str(uuid.uuid4())
        
        game_states[game_id] = {
            "api_key": request.api_key,
            "all_events": game_data["all_events"],
            "player_events": game_data["player_events"],
            "impostor_data": game_data["impostor_data"],
            "impostor_color": game_data["impostor_color"],
            "chat_histories": {
                "red": [],
                "yellow": [],
                "blue": [],
                "green": []
            }
        }
        
        for color in ["red", "yellow", "blue", "green"]:
            session = create_game_session(db, f"Player session for {color}")
            if "session_ids" not in game_states[game_id]:
                game_states[game_id]["session_ids"] = {}
            game_states[game_id]["session_ids"][color] = session.session_id
        
        print(f"[INIT_GAME] Game {game_id} created. Impostor: {game_data['impostor_color']}")
        
        return InitGameResponse(
            success=True,
            message="Game initialized successfully!",
            game_id=game_id,
            impostor_color=game_data["impostor_color"]
        )
        
    except Exception as e:
        print(f"[INIT_GAME] Error: {e}")
        import traceback
        traceback.print_exc()
        return InitGameResponse(
            success=False,
            message=f"Failed to initialize game: {str(e)}"
        )


@app.post("/api/game/chat", response_model=PlayerChatResponse)
async def chat_with_player(request: PlayerChatRequest, db: Session = Depends(get_db)):
    """Send a message to a specific player and get their response"""
    game_id = request.game_id
    color = request.color.lower()
    message = request.message
    
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if color not in ["red", "yellow", "blue", "green"]:
        raise HTTPException(status_code=400, detail="Invalid player color")
    
    game_state = game_states[game_id]
    api_key = game_state["api_key"]
    
    player_name = COLOR_TO_PLAYER.get(color, "Player1")
    player_events = game_state["player_events"].get(player_name, [])
    impostor_color = game_state["impostor_color"]
    is_impostor = (color == impostor_color)
    murder_event = game_state["impostor_data"].get("murder_event", {})
    chat_history = game_state["chat_histories"].get(color, [])
    
    chat_history.append({"role": "user", "content": message})
    
    llm_service = OpenAIService(api_key)
    raw_response = llm_service.generate_response(
        player_name=player_name,
        color=color,
        player_events=player_events,
        is_impostor=is_impostor,
        murder_event=murder_event,
        player_message=message,
        chat_history=chat_history[:-1]
    )
    
    # Apply output guardrail to check for confessions
    response = apply_output_guardrail(raw_response)
    
    chat_history.append({"role": "assistant", "content": response})
    game_state["chat_histories"][color] = chat_history
    
    session_id = game_state.get("session_ids", {}).get(color)
    if session_id:
        try:
            add_chat_message(db, session_id, "user", message)
            add_chat_message(db, session_id, "assistant", response)
        except Exception as e:
            print(f"[CHAT] Warning: Could not save to DB: {e}")
    
    return PlayerChatResponse(response=response, color=color)


@app.get("/api/game/{game_id}/state")
async def get_game_state(game_id: str):
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_state = game_states[game_id]
    return {
        "game_id": game_id,
        "players": ["red", "yellow", "blue", "green"],
        "impostor_color": game_state["impostor_color"],
        "event_count": len(game_state["all_events"])
    }


@app.post("/api/game/{game_id}/verify")
async def verify_impostor_guess(game_id: str, guess: str):
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    guess = guess.lower()
    game_state = game_states[game_id]
    actual_impostor = game_state["impostor_color"]
    is_correct = (guess == actual_impostor)
    
    return {
        "guess": guess,
        "actual_impostor": actual_impostor,
        "correct": is_correct,
        "message": "You found the impostor!" if is_correct else f"Wrong! The impostor was {actual_impostor}."
    }


@app.delete("/api/game/{game_id}")
async def delete_game(game_id: str):
    if game_id in game_states:
        del game_states[game_id]
        return {"success": True, "message": "Game deleted"}
    return {"success": False, "message": "Game not found"}


@app.get("/")
async def root():
    return {"message": "Impostor.AI Game API is running", "version": "2.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)