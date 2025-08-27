from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    tenant_code: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Document schemas
class DocumentBase(BaseModel):
    title: str


class DocumentCreate(DocumentBase):
    course_id: Optional[int] = None


class Document(DocumentBase):
    id: int
    user_id: int
    filename: str
    mime_type: str
    file_size: int
    status: str
    token_count: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentChunk(BaseModel):
    id: int
    chunk_index: int
    text: str
    token_count: int
    section_title: Optional[str] = None
    page_number: Optional[int] = None
    
    class Config:
        from_attributes = True


class Flashcard(BaseModel):
    id: int
    front: str
    back: str
    difficulty: str
    tags: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Tutor schemas
class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    session_id: Optional[int] = None


class Message(MessageBase):
    id: int
    session_id: int
    role: str
    sources: Optional[List[Dict[str, Any]]] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    model_used: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    session_type: str
    title: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class Session(SessionBase):
    id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    score_delta: Optional[float] = None
    
    class Config:
        from_attributes = True


class TutorChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    level: str = "high_school"  # elementary, middle, high_school, college
    scope: Optional[Dict[str, Any]] = None


class TutorChatResponse(BaseModel):
    reply: str
    citations: List[Dict[str, Any]]
    session_id: int
    sources: List[Dict[str, Any]]


# Quiz schemas
class QuizItemBase(BaseModel):
    item_type: str
    prompt: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = "medium"


class QuizItem(QuizItemBase):
    id: int
    source_refs: Optional[List[Dict[str, Any]]] = None
    topic_tags: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizAnswerRequest(BaseModel):
    answer: str
    time_taken: Optional[float] = None


class QuizAnswerResponse(BaseModel):
    correct: bool
    explanation: str
    next_item: Optional[QuizItem] = None
    session_complete: bool = False


class BrainBoostRequest(BaseModel):
    timebox: int = 10  # minutes


class BrainBoostResponse(BaseModel):
    quiz_id: int
    items: List[QuizItem]
    estimated_time: int  # minutes


# Progress schemas
class MasteryBase(BaseModel):
    topic: str
    score: float
    practice_count: int
    streak_days: int


class Mastery(MasteryBase):
    id: int
    user_id: int
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgressOverview(BaseModel):
    total_mastery_score: float
    weak_topics: List[Mastery]
    current_streak: int
    time_saved_this_week: int  # minutes
    total_practice_time: int  # minutes
    documents_processed: int
    flashcards_created: int


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None