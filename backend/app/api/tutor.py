"""Tutor chat API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..auth import get_current_active_user
from ..models.user import User
from ..models.learning import Session as LearningSession, Message, SessionType, MessageRole, Quiz, QuizItem
from ..services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str
    session_id: Optional[int] = None
    reading_level: str = "high_school"
    course_id: Optional[int] = None
    show_steps: bool = False


class ChatResponse(BaseModel):
    """Chat response schema."""
    session_id: int
    message: str
    sources: List[dict]
    citations: List[dict]
    tokens_used: int
    model_used: str


class BrainBoostStartRequest(BaseModel):
    """Brain boost start request schema."""
    timebox_minutes: int = 10
    topic: Optional[str] = None
    difficulty: str = "intermediate"


class BrainBoostResponse(BaseModel):
    """Brain boost response schema."""
    quiz_id: int
    session_id: int
    total_questions: int
    time_limit_minutes: int
    current_question: dict


class AnswerRequest(BaseModel):
    """Answer request schema."""
    quiz_id: int
    question_id: int
    answer: str


class AnswerResponse(BaseModel):
    """Answer response schema."""
    correct: bool
    explanation: str
    score: float
    next_question: Optional[dict]
    completed: bool


@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with the AI tutor."""
    
    # Get or create session
    session = None
    if request.session_id:
        session = db.query(LearningSession).filter(
            LearningSession.id == request.session_id,
            LearningSession.user_id == current_user.id
        ).first()
    
    if not session:
        session = LearningSession(
            user_id=current_user.id,
            session_type=SessionType.TUTOR_CHAT,
            metadata={"reading_level": request.reading_level}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save user message
    user_message = Message(
        session_id=session.id,
        role=MessageRole.USER,
        content=request.message,
        reading_level=request.reading_level
    )
    db.add(user_message)
    
    try:
        # Get AI response
        ai_response = await llm_service.answer_question(
            question=request.message,
            user=current_user,
            reading_level=request.reading_level,
            course_id=request.course_id,
            show_steps=request.show_steps,
            db=db
        )
        
        # Save AI message
        ai_message = Message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=ai_response['answer'],
            sources=ai_response['sources'],
            tokens_in=0,  # Would track input tokens
            tokens_out=ai_response['tokens_used'],
            model_used=ai_response['model_used'],
            reading_level=request.reading_level
        )
        db.add(ai_message)
        db.commit()
        
        return ChatResponse(
            session_id=session.id,
            message=ai_response['answer'],
            sources=ai_response['sources'],
            citations=ai_response['citations'],
            tokens_used=ai_response['tokens_used'],
            model_used=ai_response['model_used']
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.post("/boost/start", response_model=BrainBoostResponse)
async def start_brain_boost(
    request: BrainBoostStartRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a Brain Boost session."""
    
    try:
        # Generate quiz based on user's weak areas or specified topic
        topic = request.topic or "General Review"
        
        quiz_data = await llm_service.generate_quiz(
            topic=topic,
            difficulty=request.difficulty,
            count=min(10, request.timebox_minutes),  # ~1 question per minute
        )
        
        # Create quiz record
        quiz = Quiz(
            user_id=current_user.id,
            title=quiz_data['title'],
            description=f"Brain Boost: {topic}",
            total_items=len(quiz_data['questions']),
            time_limit_minutes=request.timebox_minutes,
            source_scope={"topic": topic, "difficulty": request.difficulty}
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        # Create quiz items
        for i, question_data in enumerate(quiz_data['questions']):
            quiz_item = QuizItem(
                quiz_id=quiz.id,
                item_type=question_data['type'],
                question=question_data['question'],
                options=question_data.get('options', []),
                correct_answer=question_data['correct_answer'],
                explanation=question_data.get('explanation', ''),
                difficulty=request.difficulty
            )
            db.add(quiz_item)
        
        # Create session
        session = LearningSession(
            user_id=current_user.id,
            quiz_id=quiz.id,
            session_type=SessionType.BRAIN_BOOST,
            total_questions=quiz.total_items,
            metadata={
                "timebox_minutes": request.timebox_minutes,
                "topic": topic,
                "difficulty": request.difficulty
            }
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Get first question
        first_question = db.query(QuizItem).filter(QuizItem.quiz_id == quiz.id).first()
        
        return BrainBoostResponse(
            quiz_id=quiz.id,
            session_id=session.id,
            total_questions=quiz.total_items,
            time_limit_minutes=request.timebox_minutes,
            current_question={
                "id": first_question.id,
                "type": first_question.item_type,
                "question": first_question.question,
                "options": first_question.options,
                "points": first_question.points
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to start Brain Boost")


@router.post("/boost/answer", response_model=AnswerResponse)
async def submit_brain_boost_answer(
    request: AnswerRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit an answer for Brain Boost."""
    
    # Get quiz and question
    quiz = db.query(Quiz).filter(
        Quiz.id == request.quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    question = db.query(QuizItem).filter(
        QuizItem.id == request.question_id,
        QuizItem.quiz_id == request.quiz_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check answer
    correct = request.answer.strip().lower() == question.correct_answer.strip().lower()
    
    # Update session with answer
    session = db.query(LearningSession).filter(
        LearningSession.quiz_id == request.quiz_id,
        LearningSession.user_id == current_user.id
    ).first()
    
    if session:
        if correct:
            session.correct_answers = (session.correct_answers or 0) + 1
        
        # Calculate current score
        answered_count = (session.correct_answers or 0) + \
                        (session.total_questions - len(db.query(QuizItem).filter(
                            QuizItem.quiz_id == request.quiz_id
                        ).all()) + 1)
        
        if answered_count > 0:
            session.score = (session.correct_answers or 0) / answered_count * 100
    
    # Get next question
    answered_questions = []  # Would track in session metadata
    next_question = db.query(QuizItem).filter(
        QuizItem.quiz_id == request.quiz_id,
        QuizItem.id != request.question_id
    ).first()
    
    next_question_data = None
    completed = next_question is None
    
    if next_question:
        next_question_data = {
            "id": next_question.id,
            "type": next_question.item_type,
            "question": next_question.question,
            "options": next_question.options,
            "points": next_question.points
        }
    
    if completed and session:
        session.ended_at = datetime.utcnow()
    
    db.commit()
    
    return AnswerResponse(
        correct=correct,
        explanation=question.explanation,
        score=session.score if session else 0,
        next_question=next_question_data,
        completed=completed
    )


@router.get("/sessions")
async def get_tutor_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's tutor sessions."""
    
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id
    ).order_by(LearningSession.started_at.desc()).limit(20).all()
    
    return [
        {
            "id": session.id,
            "type": session.session_type,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "score": session.score,
            "total_questions": session.total_questions,
            "correct_answers": session.correct_answers
        }
        for session in sessions
    ]


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages from a chat session."""
    
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    
    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "sources": message.sources,
            "created_at": message.created_at.isoformat()
        }
        for message in messages
    ]