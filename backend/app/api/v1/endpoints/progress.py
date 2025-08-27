from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth.jwt import get_current_user
from app.schemas.mastery import MasteryResponse, ProgressOverview, TopicProgress, WeakTopicResponse
from app.models.user import User
from app.models.mastery import Mastery
from app.models.quiz import Quiz
from app.models.session import Session as ChatSession

router = APIRouter()

@router.get("/overview", response_model=ProgressOverview)
async def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall learning progress overview."""
    try:
        # Get mastery statistics
        masteries = db.query(Mastery).filter(
            Mastery.user_id == current_user.id
        ).all()
        
        total_topics = len(masteries)
        mastered_topics = len([m for m in masteries if m.score >= 80.0])
        weak_topics = len([m for m in masteries if m.score < 50.0])
        
        average_mastery = sum(m.score for m in masteries) / total_topics if total_topics > 0 else 0.0
        total_study_time = sum(m.time_spent_minutes for m in masteries)
        
        # Calculate streak
        current_streak = 0
        longest_streak = 0
        current_date = datetime.utcnow().date()
        
        # Get recent activity
        recent_quizzes = db.query(Quiz).filter(
            Quiz.user_id == current_user.id,
            Quiz.completed_at >= current_date - timedelta(days=7)
        ).all()
        
        recent_sessions = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.started_at >= current_date - timedelta(days=7)
        ).all()
        
        # Calculate time saved (estimate based on AI assistance)
        time_saved = len(recent_sessions) * 15  # Assume 15 minutes saved per session
        
        return ProgressOverview(
            total_topics=total_topics,
            mastered_topics=mastered_topics,
            weak_topics=weak_topics,
            average_mastery=average_mastery,
            total_study_time_minutes=total_study_time,
            current_streak_days=current_streak,
            longest_streak_days=longest_streak,
            time_saved_this_week_minutes=time_saved
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting progress overview: {str(e)}"
        )

@router.get("/topics", response_model=List[TopicProgress])
async def get_topic_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress for all topics."""
    try:
        masteries = db.query(Mastery).filter(
            Mastery.user_id == current_user.id
        ).order_by(Mastery.score.desc()).all()
        
        topic_progress = []
        for mastery in masteries:
            target_score = 90.0  # Target mastery level
            progress_percentage = min((mastery.score / target_score) * 100, 100)
            
            topic_progress.append(TopicProgress(
                topic=mastery.topic,
                subject=mastery.subject,
                current_score=mastery.score,
                target_score=target_score,
                progress_percentage=progress_percentage,
                time_spent_minutes=mastery.time_spent_minutes,
                questions_attempted=mastery.questions_attempted,
                last_practiced_at=mastery.last_practiced_at,
                next_review_at=mastery.next_review_at
            ))
        
        return topic_progress
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting topic progress: {str(e)}"
        )

@router.get("/weak-topics", response_model=List[WeakTopicResponse])
async def get_weak_topics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weak topics that need attention."""
    try:
        weak_masteries = db.query(Mastery).filter(
            Mastery.user_id == current_user.id,
            Mastery.score < 70.0
        ).order_by(Mastery.score.asc()).limit(10).all()
        
        weak_topics = []
        for mastery in weak_masteries:
            gap_percentage = 90.0 - mastery.score  # Gap to target
            suggested_practice_time = max(10, int(gap_percentage / 10))  # 10-30 minutes
            
            weak_topics.append(WeakTopicResponse(
                topic=mastery.topic,
                subject=mastery.subject,
                current_score=mastery.score,
                target_score=90.0,
                gap_percentage=gap_percentage,
                suggested_practice_time=suggested_practice_time,
                related_documents=[]  # Would be populated with related document IDs
            ))
        
        return weak_topics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting weak topics: {str(e)}"
        )

@router.get("/mastery/{topic}", response_model=MasteryResponse)
async def get_topic_mastery(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mastery details for a specific topic."""
    try:
        mastery = db.query(Mastery).filter(
            Mastery.user_id == current_user.id,
            Mastery.topic == topic
        ).first()
        
        if not mastery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic mastery not found"
            )
        
        return MasteryResponse.from_orm(mastery)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting topic mastery: {str(e)}"
        )

@router.get("/streak")
async def get_streak_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current streak information."""
    try:
        # Calculate current streak
        current_date = datetime.utcnow().date()
        current_streak = 0
        
        # Check recent days for activity
        for days_back in range(30):  # Check last 30 days
            check_date = current_date - timedelta(days=days_back)
            
            # Check for quiz activity
            quiz_activity = db.query(Quiz).filter(
                Quiz.user_id == current_user.id,
                Quiz.completed_at >= check_date,
                Quiz.completed_at < check_date + timedelta(days=1)
            ).first()
            
            # Check for chat activity
            chat_activity = db.query(ChatSession).filter(
                ChatSession.user_id == current_user.id,
                ChatSession.started_at >= check_date,
                ChatSession.started_at < check_date + timedelta(days=1)
            ).first()
            
            if quiz_activity or chat_activity:
                current_streak += 1
            else:
                break
        
        return {
            "current_streak": current_streak,
            "last_activity": check_date.isoformat() if current_streak > 0 else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting streak info: {str(e)}"
        )