from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.core.auth.jwt import get_current_user
from app.schemas.quiz import (
    BrainBoostStartRequest, BrainBoostStartResponse, QuizAnswerRequest, 
    QuizAnswerResponse, QuizResponse, QuizWithItemsResponse
)
from app.models.user import User
from app.models.quiz import Quiz, QuizItem
from app.models.mastery import Mastery
from app.services.ai_orchestrator import AIOrchestrator

router = APIRouter()

@router.post("/boost/start", response_model=BrainBoostStartResponse)
async def start_brain_boost(
    request: BrainBoostStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a Brain Boost session."""
    try:
        # Get weak topics for the user
        weak_topics = db.query(Mastery).filter(
            Mastery.user_id == current_user.id,
            Mastery.score < 70.0  # Below 70% mastery
        ).order_by(Mastery.score.asc()).limit(5).all()
        
        # If no weak topics, use general topics
        if not weak_topics:
            topics = ["general knowledge", "study skills", "learning strategies"]
        else:
            topics = [topic.topic for topic in weak_topics]
        
        # Generate quiz using AI
        ai_orchestrator = AIOrchestrator()
        questions = await ai_orchestrator.generate_quiz(
            scope=", ".join(topics),
            count=request.timebox or 10,
            level=request.difficulty or "medium"
        )
        
        # Create quiz record
        quiz = Quiz(
            user_id=current_user.id,
            title=f"Brain Boost - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            quiz_type="brain_boost",
            source_scope=json.dumps(topics),
            difficulty_level=request.difficulty or "medium",
            time_limit_minutes=request.timebox or 10,
            total_questions=len(questions),
            started_at=datetime.utcnow()
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        # Create quiz items
        quiz_items = []
        for i, question in enumerate(questions):
            quiz_item = QuizItem(
                quiz_id=quiz.id,
                question_type=question.get("type", "multiple_choice"),
                prompt=question.get("question", ""),
                options=json.dumps(question.get("options", [])),
                correct_answer=question.get("answer", ""),
                explanation=question.get("explanation", ""),
                difficulty=question.get("difficulty", "medium"),
                topic=question.get("topic", ""),
                order_index=i + 1
            )
            db.add(quiz_item)
            quiz_items.append(quiz_item)
        
        db.commit()
        
        # Format response
        items_response = []
        for item in quiz_items:
            items_response.append({
                "id": item.id,
                "question_type": item.question_type,
                "prompt": item.prompt,
                "options": item.options,
                "difficulty": item.difficulty,
                "topic": item.topic,
                "order_index": item.order_index
            })
        
        return BrainBoostStartResponse(
            quiz_id=quiz.id,
            items=items_response,
            time_limit_minutes=quiz.time_limit_minutes,
            total_questions=quiz.total_questions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting Brain Boost: {str(e)}"
        )

@router.post("/boost/answer", response_model=QuizAnswerResponse)
async def answer_brain_boost_question(
    request: QuizAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Answer a Brain Boost question."""
    try:
        # Get quiz item
        quiz_item = db.query(QuizItem).filter(
            QuizItem.id == request.item_id
        ).first()
        
        if not quiz_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Verify user owns the quiz
        quiz = db.query(Quiz).filter(
            Quiz.id == quiz_item.quiz_id,
            Quiz.user_id == current_user.id
        ).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to answer this question"
            )
        
        # Check if answer is correct
        is_correct = request.answer.lower().strip() == quiz_item.correct_answer.lower().strip()
        
        # Update quiz item
        quiz_item.user_answer = request.answer
        quiz_item.is_correct = is_correct
        
        # Update mastery for the topic
        if quiz_item.topic:
            mastery = db.query(Mastery).filter(
                Mastery.user_id == current_user.id,
                Mastery.topic == quiz_item.topic
            ).first()
            
            if not mastery:
                mastery = Mastery(
                    user_id=current_user.id,
                    topic=quiz_item.topic,
                    score=0.0,
                    questions_attempted=0,
                    questions_correct=0
                )
                db.add(mastery)
            
            mastery.questions_attempted += 1
            if is_correct:
                mastery.questions_correct += 1
            
            # Update score (simple percentage)
            mastery.score = (mastery.questions_correct / mastery.questions_attempted) * 100
            mastery.last_practiced_at = datetime.utcnow()
        
        db.commit()
        
        # Get next question
        next_item = db.query(QuizItem).filter(
            QuizItem.quiz_id == quiz.id,
            QuizItem.order_index > quiz_item.order_index,
            QuizItem.user_answer.is_(None)
        ).order_by(QuizItem.order_index).first()
        
        # Check if quiz is completed
        total_answered = db.query(QuizItem).filter(
            QuizItem.quiz_id == quiz.id,
            QuizItem.user_answer.isnot(None)
        ).count()
        
        quiz_completed = total_answered >= quiz.total_questions
        
        if quiz_completed:
            # Calculate final score
            correct_answers = db.query(QuizItem).filter(
                QuizItem.quiz_id == quiz.id,
                QuizItem.is_correct == True
            ).count()
            
            final_score = (correct_answers / quiz.total_questions) * 100
            
            # Update quiz
            quiz.score = final_score
            quiz.completed_at = datetime.utcnow()
            quiz.time_taken_seconds = int((datetime.utcnow() - quiz.started_at).total_seconds())
        
        db.commit()
        
        # Format next item response
        next_item_response = None
        if next_item:
            next_item_response = {
                "id": next_item.id,
                "question_type": next_item.question_type,
                "prompt": next_item.prompt,
                "options": next_item.options,
                "difficulty": next_item.difficulty,
                "topic": next_item.topic,
                "order_index": next_item.order_index
            }
        
        return QuizAnswerResponse(
            correct=is_correct,
            explanation=quiz_item.explanation if is_correct else None,
            next_item=next_item_response,
            quiz_completed=quiz_completed,
            final_score=quiz.score if quiz_completed else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error answering question: {str(e)}"
        )

@router.get("/history", response_model=List[QuizResponse])
async def get_quiz_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz history for the current user."""
    quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id
    ).order_by(Quiz.created_at.desc()).limit(20).all()
    
    return [QuizResponse.from_orm(quiz) for quiz in quizzes]

@router.get("/{quiz_id}", response_model=QuizWithItemsResponse)
async def get_quiz_details(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed quiz information."""
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Get quiz items
    items = db.query(QuizItem).filter(
        QuizItem.quiz_id == quiz_id
    ).order_by(QuizItem.order_index).all()
    
    response = QuizWithItemsResponse.from_orm(quiz)
    response.items = [QuizItemResponse.from_orm(item) for item in items]
    
    return response