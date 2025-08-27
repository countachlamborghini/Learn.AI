from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    quiz_type = Column(String(50), default="brain_boost")  # brain_boost, practice, assessment
    source_scope = Column(Text, nullable=True)  # JSON string of document/course IDs
    difficulty_level = Column(String(20), default="medium")  # easy, medium, hard
    time_limit_minutes = Column(Integer, default=10)
    
    # Quiz settings
    total_questions = Column(Integer, nullable=False)
    passing_score = Column(Float, default=70.0)  # Percentage
    
    # Results
    score = Column(Float, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    items = relationship("QuizItem", back_populates="quiz")

    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}', type='{self.quiz_type}')>"

class QuizItem(Base):
    __tablename__ = "quiz_items"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Question content
    question_type = Column(String(50), nullable=False)  # multiple_choice, true_false, short_answer, essay
    prompt = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # JSON string for multiple choice
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    
    # Source references
    source_refs = Column(Text, nullable=True)  # JSON string of document/chunk references
    
    # User response
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(Float, default=1.0)
    
    # Metadata
    difficulty = Column(String(20), default="medium")
    topic = Column(String(100), nullable=True)
    order_index = Column(Integer, nullable=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="items")

    def __repr__(self):
        return f"<QuizItem(id={self.id}, quiz_id={self.quiz_id}, type='{self.question_type}')>"