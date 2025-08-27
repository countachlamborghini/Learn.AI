from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MasteryResponse(BaseModel):
    id: int
    topic: str
    subject: Optional[str] = None
    difficulty_level: str
    score: float
    confidence: float
    time_spent_minutes: int
    questions_attempted: int
    questions_correct: int
    last_seen_at: Optional[datetime] = None
    last_practiced_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None
    review_interval_days: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MasteryUpdate(BaseModel):
    score_delta: Optional[float] = None
    time_spent_minutes: Optional[int] = None
    questions_attempted: Optional[int] = None
    questions_correct: Optional[int] = None

class ProgressOverview(BaseModel):
    total_topics: int
    mastered_topics: int
    weak_topics: int
    average_mastery: float
    total_study_time_minutes: int
    current_streak_days: int
    longest_streak_days: int
    time_saved_this_week_minutes: int

class TopicProgress(BaseModel):
    topic: str
    subject: Optional[str] = None
    current_score: float
    target_score: float
    progress_percentage: float
    time_spent_minutes: int
    questions_attempted: int
    last_practiced_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None

class WeakTopicResponse(BaseModel):
    topic: str
    subject: Optional[str] = None
    current_score: float
    target_score: float
    gap_percentage: float
    suggested_practice_time: int  # minutes
    related_documents: List[int] = []  # document IDs

class MasteryTrend(BaseModel):
    date: datetime
    average_score: float
    topics_practiced: int
    time_spent_minutes: int