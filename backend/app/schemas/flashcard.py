from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CardType(str, Enum):
    QA = "qa"
    CLOZE = "cloze"
    MULTIPLE_CHOICE = "multiple_choice"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class FlashcardCreate(BaseModel):
    front: str
    back: str
    difficulty: Difficulty = Difficulty.MEDIUM
    card_type: CardType = CardType.QA
    tags: Optional[str] = None
    topic: Optional[str] = None

class FlashcardResponse(BaseModel):
    id: int
    front: str
    back: str
    difficulty: Difficulty
    card_type: CardType
    times_reviewed: int
    times_correct: int
    last_reviewed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None
    ease_factor: float
    interval: int
    repetitions: int
    tags: Optional[str] = None
    topic: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FlashcardReview(BaseModel):
    flashcard_id: int
    was_correct: bool
    review_time_seconds: Optional[int] = None

class FlashcardReviewResponse(BaseModel):
    flashcard: FlashcardResponse
    next_review_days: int
    mastery_level: float  # 0-1 scale

class FlashcardDeckResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    total_cards: int
    cards_due: int
    average_mastery: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class FlashcardDeckWithCardsResponse(FlashcardDeckResponse):
    cards: List[FlashcardResponse] = []