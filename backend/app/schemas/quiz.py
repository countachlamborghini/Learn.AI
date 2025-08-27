from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class QuizType(str, Enum):
    BRAIN_BOOST = "brain_boost"
    PRACTICE = "practice"
    ASSESSMENT = "assessment"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class QuizCreate(BaseModel):
    title: str
    quiz_type: QuizType = QuizType.BRAIN_BOOST
    source_scope: Optional[str] = None
    difficulty_level: Optional[str] = "medium"
    time_limit_minutes: Optional[int] = 10
    total_questions: int

class QuizResponse(BaseModel):
    id: int
    title: str
    quiz_type: QuizType
    source_scope: Optional[str] = None
    difficulty_level: str
    time_limit_minutes: int
    total_questions: int
    passing_score: float
    score: Optional[float] = None
    completed_at: Optional[datetime] = None
    time_taken_seconds: Optional[int] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class QuizItemCreate(BaseModel):
    question_type: QuestionType
    prompt: str
    options: Optional[str] = None  # JSON string for multiple choice
    correct_answer: str
    explanation: Optional[str] = None
    source_refs: Optional[str] = None
    difficulty: Optional[str] = "medium"
    topic: Optional[str] = None
    order_index: int

class QuizItemResponse(BaseModel):
    id: int
    question_type: QuestionType
    prompt: str
    options: Optional[str] = None
    correct_answer: str
    explanation: Optional[str] = None
    source_refs: Optional[str] = None
    difficulty: str
    topic: Optional[str] = None
    order_index: int
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    points_earned: float
    
    class Config:
        from_attributes = True

class QuizAnswerRequest(BaseModel):
    item_id: int
    answer: str

class QuizAnswerResponse(BaseModel):
    correct: bool
    explanation: Optional[str] = None
    next_item: Optional[QuizItemResponse] = None
    quiz_completed: bool = False
    final_score: Optional[float] = None

class BrainBoostStartRequest(BaseModel):
    timebox: Optional[int] = 10  # minutes
    topics: Optional[List[str]] = None
    difficulty: Optional[str] = "medium"

class BrainBoostStartResponse(BaseModel):
    quiz_id: int
    items: List[QuizItemResponse]
    time_limit_minutes: int
    total_questions: int

class QuizWithItemsResponse(QuizResponse):
    items: List[QuizItemResponse] = []