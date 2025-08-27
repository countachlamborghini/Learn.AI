from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SessionType(str, Enum):
    TUTOR_CHAT = "tutor_chat"
    BRAIN_BOOST = "brain_boost"
    PRACTICE = "practice"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class SessionCreate(BaseModel):
    session_type: SessionType
    title: Optional[str] = None
    difficulty_level: Optional[str] = "medium"
    subject_focus: Optional[str] = None
    source_scope: Optional[str] = None

class SessionResponse(BaseModel):
    id: int
    session_type: SessionType
    title: Optional[str] = None
    is_active: bool
    started_at: datetime
    ended_at: Optional[datetime] = None
    difficulty_level: str
    subject_focus: Optional[str] = None
    source_scope: Optional[str] = None
    total_messages: int
    total_tokens_used: int
    score_delta: Optional[float] = None
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str
    role: MessageRole = MessageRole.USER

class MessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    model_used: Optional[str] = None
    tokens_in: int
    tokens_out: int
    sources: Optional[str] = None
    helpfulness_rating: Optional[int] = None
    feedback_comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    level: Optional[str] = "medium"  # easy, medium, hard, kid, ap, college
    scope: Optional[str] = None  # JSON string of document/course IDs

class ChatResponse(BaseModel):
    reply: str
    session_id: int
    message_id: int
    citations: List[Dict[str, Any]] = []
    tokens_used: int
    model_used: str

class SessionWithMessagesResponse(SessionResponse):
    messages: List[MessageResponse] = []