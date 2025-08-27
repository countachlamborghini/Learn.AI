"""Progress tracking API routes."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models.user import User
from ..models.learning import LearningSession, Mastery, SessionType
from ..models.document import Document

router = APIRouter()


@router.get("/overview")
async def get_progress_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's progress overview."""
    
    # Calculate streak (simplified - would use proper date logic)
    recent_sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id,
        LearningSession.ended_at.isnot(None),
        LearningSession.started_at >= datetime.utcnow() - timedelta(days=30)
    ).order_by(desc(LearningSession.started_at)).all()
    
    # Calculate current streak
    current_streak = 0
    if recent_sessions:
        # Simplified streak calculation
        session_dates = set()
        for session in recent_sessions:
            session_dates.add(session.started_at.date())
        
        # Count consecutive days from today
        current_date = datetime.utcnow().date()
        while current_date in session_dates:
            current_streak += 1
            current_date -= timedelta(days=1)
    
    # Total study time (in minutes)
    total_study_time = 0
    for session in recent_sessions:
        if session.ended_at:
            duration = (session.ended_at - session.started_at).total_seconds() / 60
            total_study_time += duration
    
    # Documents processed
    total_documents = db.query(Document).filter(
        Document.user_id == current_user.id,
        Document.status == "completed"
    ).count()
    
    # Total flashcards created
    total_flashcards = db.query(func.count()).select_from(
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .join(Document.flashcards)
    ).scalar() or 0
    
    # Brain Boost stats
    brain_boost_sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id,
        LearningSession.session_type == SessionType.BRAIN_BOOST,
        LearningSession.ended_at.isnot(None)
    ).all()
    
    brain_boost_average_score = 0
    if brain_boost_sessions:
        scores = [s.score for s in brain_boost_sessions if s.score is not None]
        if scores:
            brain_boost_average_score = sum(scores) / len(scores)
    
    return {
        "current_streak": current_streak,
        "total_study_time_minutes": round(total_study_time),
        "total_documents": total_documents,
        "total_flashcards": total_flashcards,
        "brain_boost_sessions_completed": len(brain_boost_sessions),
        "brain_boost_average_score": round(brain_boost_average_score, 1),
        "this_week": {
            "study_sessions": len([s for s in recent_sessions if s.started_at >= datetime.utcnow() - timedelta(days=7)]),
            "study_time_minutes": round(sum([
                (s.ended_at - s.started_at).total_seconds() / 60 
                for s in recent_sessions 
                if s.ended_at and s.started_at >= datetime.utcnow() - timedelta(days=7)
            ])),
            "brain_boosts_completed": len([
                s for s in brain_boost_sessions 
                if s.started_at >= datetime.utcnow() - timedelta(days=7)
            ])
        }
    }


@router.get("/topics")
async def get_topic_mastery(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get user's topic mastery levels."""
    
    mastery_records = db.query(Mastery).filter(
        Mastery.user_id == current_user.id
    ).order_by(desc(Mastery.score)).all()
    
    # If no mastery records, create some example ones based on documents
    if not mastery_records:
        documents = db.query(Document).filter(
            Document.user_id == current_user.id,
            Document.status == "completed"
        ).all()
        
        # Extract topics from document names (simplified)
        topics = set()
        for doc in documents:
            filename = doc.original_filename.lower()
            if "math" in filename or "calculus" in filename or "algebra" in filename:
                topics.add("Mathematics")
            elif "physics" in filename:
                topics.add("Physics")
            elif "chemistry" in filename:
                topics.add("Chemistry")
            elif "biology" in filename:
                topics.add("Biology")
            elif "history" in filename:
                topics.add("History")
            elif "english" in filename or "literature" in filename:
                topics.add("English Literature")
            else:
                topics.add("General Studies")
        
        # Create initial mastery records
        for topic in topics:
            mastery = Mastery(
                user_id=current_user.id,
                topic=topic,
                score=50.0,  # Starting score
                confidence=0.5,
                review_count=0,
                streak_days=0
            )
            db.add(mastery)
        
        db.commit()
        
        # Fetch the newly created records
        mastery_records = db.query(Mastery).filter(
            Mastery.user_id == current_user.id
        ).order_by(desc(Mastery.score)).all()
    
    return [
        {
            "topic": record.topic,
            "mastery_score": round(record.score, 1),
            "confidence": round(record.confidence, 2),
            "last_reviewed": record.last_reviewed_at.isoformat() if record.last_reviewed_at else None,
            "review_count": record.review_count,
            "streak_days": record.streak_days,
            "next_review": record.next_review_at.isoformat() if record.next_review_at else None,
            "status": "strong" if record.score >= 80 else "good" if record.score >= 60 else "needs_work"
        }
        for record in mastery_records
    ]


@router.get("/weak-areas")
async def get_weak_areas(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get user's weak areas that need attention."""
    
    weak_topics = db.query(Mastery).filter(
        Mastery.user_id == current_user.id,
        Mastery.score < 70  # Threshold for "weak"
    ).order_by(Mastery.score).limit(5).all()
    
    return [
        {
            "topic": record.topic,
            "mastery_score": round(record.score, 1),
            "priority": "high" if record.score < 40 else "medium" if record.score < 60 else "low",
            "last_reviewed": record.last_reviewed_at.isoformat() if record.last_reviewed_at else None,
            "recommended_action": "Take a Brain Boost" if record.review_count < 3 else "Review materials"
        }
        for record in weak_topics
    ]


@router.get("/activity")
async def get_activity_history(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get user's activity history."""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id,
        LearningSession.started_at >= start_date
    ).order_by(desc(LearningSession.started_at)).all()
    
    activity = []
    for session in sessions:
        duration_minutes = 0
        if session.ended_at:
            duration_minutes = (session.ended_at - session.started_at).total_seconds() / 60
        
        activity.append({
            "id": session.id,
            "type": session.session_type,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "duration_minutes": round(duration_minutes),
            "score": session.score,
            "questions_answered": session.total_questions,
            "correct_answers": session.correct_answers
        })
    
    return activity


@router.get("/stats")
async def get_detailed_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed statistics for the user."""
    
    # Time-based stats
    now = datetime.utcnow()
    this_week = now - timedelta(days=7)
    this_month = now - timedelta(days=30)
    
    sessions_this_week = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id,
        LearningSession.started_at >= this_week
    ).all()
    
    sessions_this_month = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id,
        LearningSession.started_at >= this_month
    ).all()
    
    # Calculate study time
    def calculate_study_time(sessions):
        total_minutes = 0
        for session in sessions:
            if session.ended_at:
                duration = (session.ended_at - session.started_at).total_seconds() / 60
                total_minutes += duration
        return round(total_minutes)
    
    # Performance stats
    brain_boost_sessions = [s for s in sessions_this_month if s.session_type == SessionType.BRAIN_BOOST and s.score is not None]
    avg_score = sum(s.score for s in brain_boost_sessions) / len(brain_boost_sessions) if brain_boost_sessions else 0
    
    # Consistency (days studied in last 30 days)
    study_dates = set()
    for session in sessions_this_month:
        study_dates.add(session.started_at.date())
    
    return {
        "study_time": {
            "this_week_minutes": calculate_study_time(sessions_this_week),
            "this_month_minutes": calculate_study_time(sessions_this_month),
            "average_session_minutes": round(calculate_study_time(sessions_this_month) / len(sessions_this_month)) if sessions_this_month else 0
        },
        "performance": {
            "average_brain_boost_score": round(avg_score, 1),
            "total_questions_answered": sum(s.total_questions for s in sessions_this_month if s.total_questions),
            "total_correct_answers": sum(s.correct_answers for s in sessions_this_month if s.correct_answers),
            "accuracy_percentage": round(
                (sum(s.correct_answers for s in sessions_this_month if s.correct_answers) / 
                 sum(s.total_questions for s in sessions_this_month if s.total_questions)) * 100
            ) if sum(s.total_questions for s in sessions_this_month if s.total_questions) > 0 else 0
        },
        "consistency": {
            "days_studied_this_month": len(study_dates),
            "consistency_percentage": round((len(study_dates) / 30) * 100, 1),
            "longest_streak": current_user.id  # Placeholder - would calculate actual streak
        },
        "content": {
            "documents_uploaded": db.query(Document).filter(Document.user_id == current_user.id).count(),
            "flashcards_created": db.query(func.count()).select_from(
                db.query(Document)
                .filter(Document.user_id == current_user.id)
                .join(Document.flashcards)
            ).scalar() or 0,
            "brain_boosts_completed": len([s for s in sessions_this_month if s.session_type == SessionType.BRAIN_BOOST and s.ended_at])
        }
    }