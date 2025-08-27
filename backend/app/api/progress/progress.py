from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.tutor import Mastery
from app.services.progress_service import ProgressService
from app.api.schemas import ProgressOverview, Mastery as MasterySchema

router = APIRouter()


@router.get("/overview", response_model=ProgressOverview)
async def get_progress_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive progress overview"""
    return ProgressService.get_progress_overview(current_user.id, db)


@router.get("/topics", response_model=List[MasterySchema])
async def get_topic_mastery(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mastery scores for all topics"""
    return ProgressService.get_topic_mastery(current_user.id, db)


@router.get("/analytics")
async def get_learning_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed learning analytics"""
    return ProgressService.get_learning_analytics(current_user.id, days, db)


@router.get("/streak")
async def get_current_streak(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current study streak"""
    streak = ProgressService.calculate_current_streak(current_user.id, db)
    return {"current_streak": streak}


@router.get("/stats")
async def get_learning_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get key learning statistics"""
    overview = ProgressService.get_progress_overview(current_user.id, db)
    
    return {
        "total_mastery_score": overview["total_mastery_score"],
        "current_streak": overview["current_streak"],
        "time_saved_this_week": overview["time_saved_this_week"],
        "total_practice_time": overview["total_practice_time"],
        "documents_processed": overview["documents_processed"],
        "flashcards_created": overview["flashcards_created"],
        "weak_topics_count": len(overview["weak_topics"])
    }