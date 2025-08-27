from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Mastery(Base):
    __tablename__ = "mastery"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Topic identification
    topic = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=True)
    difficulty_level = Column(String(20), default="medium")
    
    # Mastery metrics
    score = Column(Float, default=0.0)  # 0-100 scale
    confidence = Column(Float, default=0.0)  # 0-1 scale
    time_spent_minutes = Column(Integer, default=0)
    
    # Learning progress
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    last_seen_at = Column(DateTime, nullable=True)
    last_practiced_at = Column(DateTime, nullable=True)
    
    # Spaced repetition data
    next_review_at = Column(DateTime, nullable=True)
    review_interval_days = Column(Integer, default=1)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="masteries")

    def __repr__(self):
        return f"<Mastery(id={self.id}, user_id={self.user_id}, topic='{self.topic}', score={self.score})>"