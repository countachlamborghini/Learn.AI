from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=True)
    
    # Flashcard content
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    card_type = Column(String(50), default="qa")  # qa, cloze, multiple_choice
    
    # Learning progress
    times_reviewed = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, nullable=True)  # For spaced repetition
    
    # Spaced repetition algorithm data
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=1)  # Days until next review
    repetitions = Column(Integer, default=0)
    
    # Metadata
    tags = Column(Text, nullable=True)  # JSON string of tags
    topic = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="flashcards")
    chunk = relationship("DocumentChunk", back_populates="flashcards")

    def __repr__(self):
        return f"<Flashcard(id={self.id}, difficulty='{self.difficulty}', type='{self.card_type}')>"