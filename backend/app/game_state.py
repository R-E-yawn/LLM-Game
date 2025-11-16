from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.models import GameSession, ChatMessage
import uuid

def create_game_session(db: Session, scenario: str) -> GameSession:
    """Create a new game session"""
    session_id = str(uuid.uuid4())
    
    game_session = GameSession(
        session_id=session_id,
        scenario=scenario,
        health=100,
        coins=0
    )
    
    db.add(game_session)
    db.commit()
    db.refresh(game_session)
    
    return game_session

def get_game_session(db: Session, session_id: str) -> Optional[GameSession]:
    """Get game session by session_id"""
    return db.query(GameSession).filter(GameSession.session_id == session_id).first()

def update_game_stats(db: Session, session_id: str, stats: Dict[str, int]) -> Optional[GameSession]:
    """Update game session stats"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        return None
    
    if "health" in stats:
        game_session.health = stats["health"]
    if "coins" in stats:
        game_session.coins = stats["coins"]
    
    db.commit()
    db.refresh(game_session)
    return game_session

def add_chat_message(
    db: Session, 
    session_id: str, 
    role: str, 
    content: str
) -> ChatMessage:
    """Add a chat message to the session"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        raise ValueError(f"Session {session_id} not found")
    
    message = ChatMessage(
        session_id=game_session.id,
        role=role,
        content=content
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_chat_messages(db: Session, session_id: str) -> list:
    """Get all chat messages for a session"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        return []
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == game_session.id
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
        }
        for msg in messages
    ]

def get_summary_message(db: Session, session_id: str) -> Optional[str]:
    """Get the compressed summary message if it exists"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        return None
    
    summary_msg = db.query(ChatMessage).filter(
        ChatMessage.session_id == game_session.id,
        ChatMessage.role == "summary"
    ).first()
    
    return summary_msg.content if summary_msg else None

def store_summary_message(db: Session, session_id: str, summary: str) -> ChatMessage:
    """Store or update the compressed summary message"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        raise ValueError(f"Session {session_id} not found")
    
    # Check if summary already exists
    existing_summary = db.query(ChatMessage).filter(
        ChatMessage.session_id == game_session.id,
        ChatMessage.role == "summary"
    ).first()
    
    if existing_summary:
        # Update existing summary
        existing_summary.content = summary
        db.commit()
        db.refresh(existing_summary)
        return existing_summary
    else:
        # Create new summary message
        summary_msg = ChatMessage(
            session_id=game_session.id,
            role="summary",
            content=summary
        )
        db.add(summary_msg)
        db.commit()
        db.refresh(summary_msg)
        return summary_msg

def delete_messages_before(db: Session, session_id: str, message_id: int):
    """Delete all regular messages (user/assistant) before a given message ID"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        return
    
    # Delete all user/assistant messages before this message (excluding summary)
    db.query(ChatMessage).filter(
        ChatMessage.session_id == game_session.id,
        ChatMessage.id < message_id,
        ChatMessage.role.in_(["user", "assistant"])
    ).delete()
    
    db.commit()

def get_uncompressed_messages(db: Session, session_id: str) -> list:
    """Get messages that haven't been compressed yet (excludes summary, returns user/assistant only)"""
    game_session = get_game_session(db, session_id)
    if not game_session:
        return []
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == game_session.id,
        ChatMessage.role.in_(["user", "assistant"])
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            "id": msg.id
        }
        for msg in messages
    ]

