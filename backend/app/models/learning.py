"""Learning and assessment models."""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class SessionType(str, enum.Enum):
    BRAIN_BOOST = "brain_boost"
    TUTOR_CHAT = "tutor_chat"
    FLASHCARD_REVIEW = "flashcard_review"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class QuizItemType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_BLANK = "fill_blank"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Flashcard(Base):
    """Flashcard model."""
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_id = Column(Integer, ForeignKey("doc_chunks.id"), nullable=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    difficulty = Column(String, default=DifficultyLevel.INTERMEDIATE)
    topic = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="flashcards")
    chunk = relationship("DocumentChunk", back_populates="flashcards")


class Quiz(Base):
    """Quiz model."""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    source_scope = Column(JSON)  # Which documents/topics to include
    total_items = Column(Integer, default=0)
    time_limit_minutes = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    items = relationship("QuizItem", back_populates="quiz", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="quiz")


class QuizItem(Base):
    """Quiz item model."""
    __tablename__ = "quiz_items"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    item_type = Column(String, default=QuizItemType.MULTIPLE_CHOICE)
    question = Column(Text, nullable=False)
    options = Column(JSON)  # For multiple choice
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    source_refs = Column(JSON, default=[])  # References to source chunks
    difficulty = Column(String, default=DifficultyLevel.INTERMEDIATE)
    points = Column(Integer, default=1)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="items")


class Session(Base):
    """Learning session model."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=True)
    session_type = Column(String, default=SessionType.TUTOR_CHAT)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    score = Column(Float)
    score_delta = Column(Float)  # Change from previous attempts
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    metadata = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    quiz = relationship("Quiz", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Chat message model."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    role = Column(String, default=MessageRole.USER)
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=[])  # Source citations
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    model_used = Column(String)
    reading_level = Column(String, default="high_school")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="messages")


class Mastery(Base):
    """Topic mastery tracking."""
    __tablename__ = "mastery"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String, nullable=False)
    score = Column(Float, default=0.0)  # 0-100 mastery score
    confidence = Column(Float, default=0.0)  # Confidence level
    last_reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    review_count = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    next_review_at = Column(DateTime(timezone=True))  # Spaced repetition
    
    # Relationships
    user = relationship("User", back_populates="mastery_records")