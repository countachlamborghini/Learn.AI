from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.tutor import Mastery, Session as TutorSession, QuizAnswer
from app.models.document import Document, Flashcard
from app.models.user import User


class ProgressService:
    
    @staticmethod
    def get_progress_overview(user_id: int, db: Session) -> Dict[str, Any]:
        """Get comprehensive progress overview for a user"""
        
        # Calculate total mastery score
        mastery_records = db.query(Mastery).filter(Mastery.user_id == user_id).all()
        total_mastery_score = sum(record.score for record in mastery_records) / len(mastery_records) if mastery_records else 0.0
        
        # Get weak topics (score < 0.6)
        weak_topics = db.query(Mastery).filter(
            and_(Mastery.user_id == user_id, Mastery.score < 0.6)
        ).order_by(Mastery.score.asc()).limit(5).all()
        
        # Calculate current streak
        current_streak = ProgressService.calculate_current_streak(user_id, db)
        
        # Calculate time saved this week
        time_saved_this_week = ProgressService.calculate_time_saved_this_week(user_id, db)
        
        # Calculate total practice time
        total_practice_time = ProgressService.calculate_total_practice_time(user_id, db)
        
        # Count documents and flashcards
        documents_processed = db.query(Document).filter(Document.user_id == user_id).count()
        flashcards_created = db.query(Flashcard).join(Flashcard.document).filter(
            Flashcard.document.has(user_id=user_id)
        ).count()
        
        return {
            "total_mastery_score": total_mastery_score,
            "weak_topics": weak_topics,
            "current_streak": current_streak,
            "time_saved_this_week": time_saved_this_week,
            "total_practice_time": total_practice_time,
            "documents_processed": documents_processed,
            "flashcards_created": flashcards_created
        }
    
    @staticmethod
    def calculate_current_streak(user_id: int, db: Session) -> int:
        """Calculate current study streak in days"""
        
        # Get all sessions in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sessions = db.query(TutorSession).filter(
            and_(
                TutorSession.user_id == user_id,
                TutorSession.started_at >= thirty_days_ago
            )
        ).order_by(TutorSession.started_at.desc()).all()
        
        if not sessions:
            return 0
        
        # Group sessions by date
        session_dates = set()
        for session in sessions:
            session_dates.add(session.started_at.date())
        
        # Calculate consecutive days
        current_date = datetime.utcnow().date()
        streak = 0
        
        for i in range(30):
            check_date = current_date - timedelta(days=i)
            if check_date in session_dates:
                streak += 1
            else:
                break
        
        return streak
    
    @staticmethod
    def calculate_time_saved_this_week(user_id: int, db: Session) -> int:
        """Calculate estimated time saved this week through AI assistance"""
        
        # Get sessions from this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        sessions = db.query(TutorSession).filter(
            and_(
                TutorSession.user_id == user_id,
                TutorSession.started_at >= week_ago
            )
        ).all()
        
        # Estimate time saved based on session types
        time_saved = 0
        for session in sessions:
            if session.session_type == "tutor_chat":
                # Estimate 5 minutes saved per chat session
                time_saved += 5
            elif session.session_type == "brain_boost":
                # Estimate 3 minutes saved per brain boost
                time_saved += 3
        
        return time_saved
    
    @staticmethod
    def calculate_total_practice_time(user_id: int, db: Session) -> int:
        """Calculate total practice time in minutes"""
        
        # Get all completed sessions
        sessions = db.query(TutorSession).filter(
            and_(
                TutorSession.user_id == user_id,
                TutorSession.ended_at.isnot(None)
            )
        ).all()
        
        total_minutes = 0
        for session in sessions:
            if session.started_at and session.ended_at:
                duration = session.ended_at - session.started_at
                total_minutes += int(duration.total_seconds() / 60)
        
        return total_minutes
    
    @staticmethod
    def update_mastery(user_id: int, topic: str, score_delta: float, db: Session):
        """Update mastery score for a topic"""
        
        mastery = db.query(Mastery).filter(
            and_(Mastery.user_id == user_id, Mastery.topic == topic)
        ).first()
        
        if mastery:
            # Update existing mastery
            mastery.score = min(1.0, max(0.0, mastery.score + score_delta))
            mastery.practice_count += 1
            mastery.last_seen_at = datetime.utcnow()
            
            # Update streak if practiced today
            today = datetime.utcnow().date()
            last_practice = mastery.last_seen_at.date()
            if last_practice == today:
                mastery.streak_days += 1
            elif last_practice < today - timedelta(days=1):
                mastery.streak_days = 1
        else:
            # Create new mastery record
            mastery = Mastery(
                user_id=user_id,
                topic=topic,
                score=max(0.0, score_delta),
                practice_count=1,
                streak_days=1
            )
            db.add(mastery)
        
        db.commit()
        return mastery
    
    @staticmethod
    def get_topic_mastery(user_id: int, db: Session) -> List[Mastery]:
        """Get mastery scores for all topics"""
        
        mastery_records = db.query(Mastery).filter(
            Mastery.user_id == user_id
        ).order_by(Mastery.score.desc()).all()
        
        return mastery_records
    
    @staticmethod
    def get_learning_analytics(user_id: int, days: int = 30, db: Session) -> Dict[str, Any]:
        """Get detailed learning analytics"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Session analytics
        sessions = db.query(TutorSession).filter(
            and_(
                TutorSession.user_id == user_id,
                TutorSession.started_at >= start_date
            )
        ).all()
        
        session_types = {}
        for session in sessions:
            session_type = session.session_type
            if session_type not in session_types:
                session_types[session_type] = 0
            session_types[session_type] += 1
        
        # Quiz performance
        quiz_answers = db.query(QuizAnswer).join(QuizAnswer.quiz_item).join(
            QuizAnswer.quiz_item.session
        ).filter(
            and_(
                QuizAnswer.user_id == user_id,
                QuizAnswer.created_at >= start_date
            )
        ).all()
        
        total_questions = len(quiz_answers)
        correct_answers = sum(1 for answer in quiz_answers if answer.is_correct)
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Daily activity
        daily_activity = {}
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            daily_activity[date.isoformat()] = 0
        
        for session in sessions:
            date = session.started_at.date()
            if date.isoformat() in daily_activity:
                daily_activity[date.isoformat()] += 1
        
        return {
            "session_types": session_types,
            "quiz_performance": {
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "accuracy_percentage": accuracy
            },
            "daily_activity": daily_activity,
            "total_sessions": len(sessions)
        }