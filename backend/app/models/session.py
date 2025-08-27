from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(50), nullable=False)  # tutor_chat, brain_boost, practice
    title = Column(String(255), nullable=True)
    
    # Session state
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    
    # Session metadata
    difficulty_level = Column(String(20), default="medium")  # easy, medium, hard
    subject_focus = Column(String(100), nullable=True)
    source_scope = Column(Text, nullable=True)  # JSON string of document/course IDs
    
    # Analytics
    total_messages = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    score_delta = Column(Float, nullable=True)  # Learning progress
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, type='{self.session_type}')>"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # AI model info
    model_used = Column(String(100), nullable=True)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    
    # Source citations
    sources = Column(Text, nullable=True)  # JSON string of source references
    
    # User feedback
    helpfulness_rating = Column(Integer, nullable=True)  # 1-5 scale
    feedback_comment = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, session_id={self.session_id}, role='{self.role}')>"