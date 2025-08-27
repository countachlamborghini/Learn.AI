from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.tutor import Session as TutorSession, Message, QuizItem, QuizAnswer
from app.services.tutor_service import TutorService
from app.api.schemas import (
    TutorChatRequest, TutorChatResponse, BrainBoostRequest, BrainBoostResponse,
    QuizAnswerRequest, QuizAnswerResponse, Session as SessionSchema, Message as MessageSchema
)

router = APIRouter()


@router.post("/chat", response_model=TutorChatResponse)
async def chat_with_tutor(
    request: TutorChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with the AI tutor"""
    try:
        response = await TutorService.chat_with_tutor(
            user_id=current_user.id,
            message=request.message,
            session_id=request.session_id,
            level=request.level,
            scope=request.scope,
            db=db
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/boost/start", response_model=BrainBoostResponse)
async def start_brain_boost(
    request: BrainBoostRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a Brain Boost session"""
    try:
        response = await TutorService.start_brain_boost(
            user_id=current_user.id,
            timebox=request.timebox,
            db=db
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/boost/answer", response_model=QuizAnswerResponse)
async def answer_brain_boost_question(
    quiz_id: int,
    item_id: int,
    answer_request: QuizAnswerRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Answer a Brain Boost question"""
    
    # Verify session ownership
    session = db.query(TutorSession).filter(
        TutorSession.id == quiz_id,
        TutorSession.user_id == current_user.id,
        TutorSession.session_type == "brain_boost"
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Brain Boost session not found")
    
    # Get the quiz item
    quiz_item = db.query(QuizItem).filter(
        QuizItem.session_id == quiz_id,
        QuizItem.id == item_id
    ).first()
    
    if not quiz_item:
        raise HTTPException(status_code=404, detail="Quiz item not found")
    
    # Simple answer checking (in production, use more sophisticated grading)
    is_correct = answer_request.answer.lower().strip() in quiz_item.correct_answer.lower()
    
    # Save the answer
    quiz_answer = QuizAnswer(
        quiz_item_id=quiz_item.id,
        user_id=current_user.id,
        answer=answer_request.answer,
        is_correct=is_correct,
        time_taken=answer_request.time_taken
    )
    db.add(quiz_answer)
    
    # Get next item
    next_item = db.query(QuizItem).filter(
        QuizItem.session_id == quiz_id,
        QuizItem.id > item_id
    ).first()
    
    session_complete = next_item is None
    
    if session_complete:
        session.ended_at = db.query(db.func.now()).scalar()
        db.commit()
    
    return {
        "correct": is_correct,
        "explanation": quiz_item.explanation or "Good effort! Keep practicing.",
        "next_item": next_item,
        "session_complete": session_complete
    }


@router.get("/sessions", response_model=List[SessionSchema])
async def list_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's tutor sessions"""
    sessions = db.query(TutorSession).filter(
        TutorSession.user_id == current_user.id
    ).order_by(TutorSession.started_at.desc()).all()
    
    return sessions


@router.get("/sessions/{session_id}/messages", response_model=List[MessageSchema])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific session"""
    # Verify session ownership
    session = db.query(TutorSession).filter(
        TutorSession.id == session_id,
        TutorSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    
    return messages


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a session"""
    session = db.query(TutorSession).filter(
        TutorSession.id == session_id,
        TutorSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}