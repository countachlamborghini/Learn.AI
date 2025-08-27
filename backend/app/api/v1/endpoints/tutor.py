from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.core.auth.jwt import get_current_user
from app.schemas.session import ChatRequest, ChatResponse, SessionResponse, SessionWithMessagesResponse, MessageResponse
from app.models.user import User
from app.models.session import Session as ChatSession, Message
from app.services.ai_orchestrator import AIOrchestrator

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with the AI tutor."""
    try:
        # Get or create session
        session = None
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id,
                ChatSession.is_active == True
            ).first()
        
        if not session:
            session = ChatSession(
                user_id=current_user.id,
                session_type="tutor_chat",
                difficulty_level=request.level,
                source_scope=request.scope
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Save user message
        user_message = Message(
            session_id=session.id,
            role="user",
            content=request.message,
            tokens_in=len(request.message.split())  # Rough estimate
        )
        db.add(user_message)
        db.commit()
        
        # Get AI response
        ai_orchestrator = AIOrchestrator()
        response = await ai_orchestrator.answer_question(
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            query=request.message,
            level=request.level,
            scope=request.scope,
            session_id=session.id
        )
        
        # Save AI response
        ai_message = Message(
            session_id=session.id,
            role="assistant",
            content=response["answer"],
            model_used=response["model_used"],
            tokens_in=response["tokens_used"],
            sources=json.dumps(response["sources"]) if response["sources"] else None
        )
        db.add(ai_message)
        
        # Update session stats
        session.total_messages += 2
        session.total_tokens_used += response["tokens_used"]
        session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ai_message)
        
        return ChatResponse(
            reply=response["answer"],
            session_id=session.id,
            message_id=ai_message.id,
            citations=response["sources"],
            tokens_used=response["tokens_used"],
            model_used=response["model_used"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat: {str(e)}"
        )

@router.get("/sessions", response_model=List[SessionResponse])
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions for the current user."""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.session_type == "tutor_chat"
    ).order_by(ChatSession.started_at.desc()).all()
    
    return [SessionResponse.from_orm(session) for session in sessions]

@router.get("/sessions/{session_id}", response_model=SessionWithMessagesResponse)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat session with all messages."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
        ChatSession.session_type == "tutor_chat"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get messages
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    
    response = SessionWithMessagesResponse.from_orm(session)
    response.messages = [MessageResponse.from_orm(msg) for msg in messages]
    
    return response

@router.post("/sessions/{session_id}/end")
async def end_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End a chat session."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
        ChatSession.session_type == "tutor_chat"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.is_active = False
    session.ended_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Session ended successfully"}

@router.post("/messages/{message_id}/feedback")
async def rate_message(
    message_id: int,
    rating: int,  # 1-5 scale
    comment: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate the helpfulness of an AI message."""
    if not 1 <= rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.role == "assistant"
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify user owns the session
    session = db.query(ChatSession).filter(
        ChatSession.id == message.session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to rate this message"
        )
    
    message.helpfulness_rating = rating
    message.feedback_comment = comment
    db.commit()
    
    return {"message": "Feedback submitted successfully"}