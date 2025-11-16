from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
import os

from app.database import get_db, init_db
from app.models import GameSession
from app.game_state import (
    create_game_session,
    get_game_session,
    update_game_stats,
    add_chat_message,
    get_chat_messages,
    get_uncompressed_messages,
    get_summary_message,
    store_summary_message,
    delete_messages_before
)
from app.llm_service import OllamaService

app = FastAPI(title="Story AI Game API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Initialize LLM service
llm_service = OllamaService()

# Request/Response models
class GameStartRequest(BaseModel):
    scenario: str

class GameStartResponse(BaseModel):
    session_id: str
    scenario: str
    stats: Dict[str, int]

class ActionRequest(BaseModel):
    action: str

class ActionResponse(BaseModel):
    message: str
    stats: Dict[str, int]

class GameStateResponse(BaseModel):
    session_id: str
    scenario: str
    stats: Dict[str, int]

class MessagesResponse(BaseModel):
    messages: list

# API Routes
@app.post("/api/game/start", response_model=GameStartResponse)
async def start_game(request: GameStartRequest, db: Session = Depends(get_db)):
    """Start a new game session"""
    try:
        game_session = create_game_session(db, request.scenario)
        
        return GameStartResponse(
            session_id=game_session.session_id,
            scenario=game_session.scenario,
            stats={
                "health": game_session.health,
                "coins": game_session.coins
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start game: {str(e)}")

@app.post("/api/game/{session_id}/action", response_model=ActionResponse)
async def send_action(
    session_id: str,
    request: ActionRequest,
    db: Session = Depends(get_db)
):
    """Send a player action and get LLM response"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Add user message to chat
    add_chat_message(db, session_id, "user", request.action)
    
    # Get uncompressed messages (only user/assistant, excludes summary)
    uncompressed_messages = get_uncompressed_messages(db, session_id)
    
    # Get existing summary if any
    existing_summary = get_summary_message(db, session_id)
    
    # Get current stats
    current_stats = {
        "health": game_session.health,
        "coins": game_session.coins
    }
    
    # Get LLM response
    try:
        llm_result = llm_service.generate_response(
            scenario=game_session.scenario,
            player_action=request.action,
            current_stats=current_stats,
            uncompressed_messages=uncompressed_messages,
            existing_summary=existing_summary
        )
        
        # Update stats
        updated_stats = llm_result.get("stats", current_stats)
        update_game_stats(db, session_id, updated_stats)
        
        # Add assistant message to chat
        assistant_msg = add_chat_message(db, session_id, "assistant", llm_result.get("message", ""))
        
        # Handle compression: store summary and delete old messages
        compressed_summary = llm_result.get("compressed_summary")
        messages_to_compress = llm_result.get("messages_to_compress", [])
        
        if compressed_summary and len(messages_to_compress) > 0:
            # Store the compressed summary
            store_summary_message(db, session_id, compressed_summary)
            
            # Delete old messages that were compressed by their IDs
            message_ids_to_delete = [msg.get("id") for msg in messages_to_compress if msg.get("id")]
            if message_ids_to_delete:
                from app.models import ChatMessage
                deleted_count = db.query(ChatMessage).filter(
                    ChatMessage.id.in_(message_ids_to_delete)
                ).delete(synchronize_session=False)
                db.commit()
                print(f"[COMPRESSION] Deleted {deleted_count} old messages, stored summary")
        
        # Refresh game session to get updated stats
        game_session = get_game_session(db, session_id)
        
        return ActionResponse(
            message=llm_result.get("message", ""),
            stats={
                "health": game_session.health,
                "coins": game_session.coins
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process action: {str(e)}")

@app.get("/api/game/{session_id}/state", response_model=GameStateResponse)
async def get_state(session_id: str, db: Session = Depends(get_db)):
    """Get current game state"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return GameStateResponse(
        session_id=game_session.session_id,
        scenario=game_session.scenario,
        stats={
            "health": game_session.health,
            "coins": game_session.coins
        }
    )

@app.get("/api/game/{session_id}/messages", response_model=MessagesResponse)
async def get_messages(session_id: str, db: Session = Depends(get_db)):
    """Get chat message history"""
    messages = get_chat_messages(db, session_id)
    return MessagesResponse(messages=messages)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Story AI Game API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

