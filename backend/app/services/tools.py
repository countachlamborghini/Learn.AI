import logging
from typing import List, Dict, Any, Optional
import json
import re

from app.services.vector_store import VectorStore
from app.services.ai_orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

# Global instances
vector_store = VectorStore()
ai_orchestrator = AIOrchestrator()

async def search_docs(query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Search documents for relevant information."""
    try:
        results = await vector_store.search(query, top_k=10, filters=filters)
        return results
    except Exception as e:
        logger.error(f"Error in search_docs: {e}")
        return []

async def get_chunks(chunk_ids: List[int]) -> List[Dict[str, Any]]:
    """Get full text of document chunks."""
    try:
        chunks = await vector_store.get_chunks_by_ids(chunk_ids)
        return chunks
    except Exception as e:
        logger.error(f"Error in get_chunks: {e}")
        return []

async def make_flashcards(text: str, level: str = "medium", count: int = 5) -> List[Dict[str, str]]:
    """Generate flashcards from text."""
    try:
        flashcards = await ai_orchestrator.generate_flashcards(text, level, count)
        return flashcards
    except Exception as e:
        logger.error(f"Error in make_flashcards: {e}")
        return []

async def make_quiz(scope: str, count: int = 5, level: str = "medium") -> List[Dict[str, Any]]:
    """Generate quiz questions."""
    try:
        questions = await ai_orchestrator.generate_quiz(scope, count, level)
        return questions
    except Exception as e:
        logger.error(f"Error in make_quiz: {e}")
        return []

async def micro_lesson(topics: List[str], timebox: int = 10, level: str = "medium") -> Dict[str, Any]:
    """Generate a micro-lesson for given topics."""
    try:
        # This would use the AI orchestrator to create a structured lesson
        lesson_content = f"Micro-lesson for {', '.join(topics)} at {level} level, {timebox} minutes"
        return {
            "title": f"Quick Review: {', '.join(topics)}",
            "duration_minutes": timebox,
            "content": lesson_content,
            "topics": topics,
            "level": level
        }
    except Exception as e:
        logger.error(f"Error in micro_lesson: {e}")
        return {}

async def math_solver(expression: str, show_steps: bool = True) -> Dict[str, Any]:
    """Solve mathematical expressions with steps."""
    try:
        # This is a simplified implementation
        # In production, you'd use a proper math library like SymPy
        
        # Basic arithmetic evaluation (for demo purposes)
        # In production, use a proper math parser
        try:
            # Simple evaluation for basic expressions
            result = eval(expression)
            steps = [f"Evaluated: {expression} = {result}"] if show_steps else []
            
            return {
                "expression": expression,
                "result": result,
                "steps": steps,
                "latex": f"${expression} = {result}$"
            }
        except:
            return {
                "expression": expression,
                "result": "Unable to evaluate",
                "steps": ["Expression could not be evaluated"],
                "latex": f"${expression}$"
            }
            
    except Exception as e:
        logger.error(f"Error in math_solver: {e}")
        return {
            "expression": expression,
            "result": "Error occurred",
            "steps": ["An error occurred while solving"],
            "latex": f"${expression}$"
        }

async def grade_answer(prompt: str, student_answer: str) -> Dict[str, Any]:
    """Grade a student's answer."""
    try:
        # This would use the AI orchestrator to grade the answer
        # For now, return a simple structure
        return {
            "score": 0.8,  # 0-1 scale
            "feedback": "Good answer! Consider adding more detail.",
            "correct_parts": ["Main concept understood"],
            "improvement_areas": ["Add examples", "Explain reasoning"]
        }
    except Exception as e:
        logger.error(f"Error in grade_answer: {e}")
        return {
            "score": 0.0,
            "feedback": "Unable to grade answer",
            "correct_parts": [],
            "improvement_areas": []
        }

async def level_adapter(text: str, target_level: str) -> str:
    """Adapt text to different reading levels."""
    try:
        # This would use the AI orchestrator to adapt the text
        # For now, return the original text with a note
        level_notes = {
            "kid": " (simplified for children)",
            "hs": " (high school level)",
            "ap": " (advanced placement level)",
            "college": " (college level)"
        }
        
        return text + level_notes.get(target_level.lower(), "")
        
    except Exception as e:
        logger.error(f"Error in level_adapter: {e}")
        return text

# Additional utility functions

async def extract_topics_from_text(text: str) -> List[str]:
    """Extract main topics from text."""
    try:
        # This would use NLP to extract topics
        # For now, return a simple list
        words = text.lower().split()
        # Simple keyword extraction
        topics = list(set([word for word in words if len(word) > 4]))
        return topics[:5]  # Return top 5 topics
    except Exception as e:
        logger.error(f"Error extracting topics: {e}")
        return []

async def calculate_difficulty(text: str) -> str:
    """Calculate the difficulty level of text."""
    try:
        # Simple heuristics for difficulty calculation
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_word_length > 8:
            return "hard"
        elif avg_word_length > 6:
            return "medium"
        else:
            return "easy"
    except Exception as e:
        logger.error(f"Error calculating difficulty: {e}")
        return "medium"

async def generate_summary(text: str, max_length: int = 200) -> str:
    """Generate a summary of text."""
    try:
        # This would use the AI orchestrator to generate a summary
        # For now, return a simple truncation
        if len(text) <= max_length:
            return text
        else:
            return text[:max_length] + "..."
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return text[:max_length] + "..." if len(text) > max_length else text