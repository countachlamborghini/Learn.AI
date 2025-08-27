from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String, nullable=False)  # tutor_chat, brain_boost, quiz
    title = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    score_delta = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional session data
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")
    quiz_items = relationship("QuizItem", back_populates="session")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Array of source references
    tokens_in = Column(Integer, nullable=True)
    tokens_out = Column(Integer, nullable=True)
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="messages")


class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    source_scope = Column(JSON, nullable=True)  # Document IDs, course IDs, etc.
    quiz_type = Column(String, default="brain_boost")  # brain_boost, custom, practice
    difficulty = Column(String, default="medium")
    time_limit = Column(Integer, nullable=True)  # in minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    items = relationship("QuizItem", back_populates="quiz")


class QuizItem(Base):
    __tablename__ = "quiz_items"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    item_type = Column(String, nullable=False)  # multiple_choice, open_ended, true_false
    prompt = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # For multiple choice
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    source_refs = Column(JSON, nullable=True)  # Array of source references
    difficulty = Column(String, default="medium")
    topic_tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="items")
    session = relationship("Session", back_populates="quiz_items")
    answers = relationship("QuizAnswer", back_populates="quiz_item")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_item_id = Column(Integer, ForeignKey("quiz_items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Float, nullable=True)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz_item = relationship("QuizItem", back_populates="answers")
    user = relationship("User")


class Mastery(Base):
    __tablename__ = "mastery"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    score = Column(Float, default=0.0)  # 0.0 to 1.0
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    practice_count = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mastery_records")