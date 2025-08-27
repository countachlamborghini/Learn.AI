"""LLM service for AI operations."""

import json
from typing import List, Dict, Any, Optional
import openai
from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import User
from .rag_service import RAGService


class LLMService:
    """Service for LLM operations."""
    
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        self.rag_service = RAGService()
    
    async def answer_question(
        self,
        question: str,
        user: User,
        reading_level: str = "high_school",
        course_id: Optional[int] = None,
        show_steps: bool = False,
        db: Session = None
    ) -> Dict[str, Any]:
        """Answer a question using RAG."""
        
        # Search for relevant context
        search_results = await self.rag_service.search_documents(
            query=question,
            user=user,
            top_k=8,
            course_id=course_id,
            db=db
        )
        
        # Build context from search results
        context = self._build_context(search_results)
        
        # Generate prompt
        prompt = self._build_answer_prompt(
            question=question,
            context=context,
            reading_level=reading_level,
            show_steps=show_steps
        )
        
        # Call LLM
        response = await self._call_llm(prompt, user)
        
        # Format response with citations
        formatted_response = self._format_response_with_citations(
            response['content'],
            search_results
        )
        
        return {
            'answer': formatted_response['answer'],
            'citations': formatted_response['citations'],
            'sources': search_results,
            'tokens_used': response['tokens_used'],
            'model_used': response['model_used']
        }
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results."""
        context_parts = []
        
        for i, result in enumerate(search_results):
            source_ref = f"[{i+1}] {result['document_name']}"
            if result['section_title']:
                source_ref += f" - {result['section_title']}"
            if result['page_number']:
                source_ref += f" (Page {result['page_number']})"
            
            context_parts.append(f"{source_ref}:\n{result['text']}\n")
        
        return "\n".join(context_parts)
    
    def _build_answer_prompt(
        self,
        question: str,
        context: str,
        reading_level: str,
        show_steps: bool
    ) -> str:
        """Build prompt for answering questions."""
        
        level_instructions = {
            "elementary": "Use simple words and short sentences. Explain like talking to a 5th grader.",
            "middle_school": "Use clear language appropriate for grades 6-8. Define technical terms.",
            "high_school": "Use vocabulary appropriate for grades 9-12. Be precise but accessible.",
            "college": "Use advanced vocabulary and concepts. Assume knowledge of prerequisites.",
            "graduate": "Use technical language and advanced concepts as appropriate."
        }
        
        level_instruction = level_instructions.get(reading_level, level_instructions["high_school"])
        
        steps_instruction = ""
        if show_steps:
            steps_instruction = """
If this is a math, science, or problem-solving question, show your work step-by-step.
Format steps clearly with numbered items or bullet points.
"""
        
        prompt = f"""You are Global Brain, an AI study companion. Your job is to help students learn by providing accurate, well-sourced answers.

INSTRUCTIONS:
1. Answer the question using ONLY the provided context
2. {level_instruction}
3. Always cite your sources using [1], [2], etc. that match the context numbering
4. If you cannot answer from the context, say "I don't have enough information in your materials to answer this question"
5. Never make up information or provide sources not in the context
{steps_instruction}

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
        
        return prompt
    
    async def _call_llm(self, prompt: str, user: User) -> Dict[str, Any]:
        """Call the LLM with the prompt."""
        try:
            # Choose model based on complexity (simplified routing)
            model = settings.default_model
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Global Brain, a helpful AI study assistant. Always cite sources and adapt to the student's level."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.max_tokens_per_request,
                temperature=settings.temperature
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'model_used': model
            }
            
        except Exception as e:
            # Fallback response
            return {
                'content': "I'm sorry, I'm having trouble processing your question right now. Please try again later.",
                'tokens_used': 0,
                'model_used': 'fallback'
            }
    
    def _format_response_with_citations(
        self, 
        response: str, 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format response with proper citations."""
        
        # Extract citation numbers from response
        import re
        citation_pattern = r'\[(\d+)\]'
        cited_numbers = set(re.findall(citation_pattern, response))
        
        # Build citations list
        citations = []
        for i, result in enumerate(search_results):
            citation_num = str(i + 1)
            if citation_num in cited_numbers:
                citations.append({
                    'number': citation_num,
                    'document_name': result['document_name'],
                    'section_title': result['section_title'],
                    'page_number': result['page_number'],
                    'chunk_id': result['chunk_id']
                })
        
        return {
            'answer': response,
            'citations': citations
        }
    
    async def generate_flashcards(
        self,
        text: str,
        reading_level: str = "high_school",
        count: int = 5
    ) -> List[Dict[str, str]]:
        """Generate flashcards from text content."""
        
        prompt = f"""Create {count} high-quality flashcards from the following text.

REQUIREMENTS:
- Make questions clear and specific
- Adapt language to {reading_level} level
- Cover the most important concepts
- Use concise but complete answers
- Format as JSON array with 'front' and 'back' fields

TEXT:
{text}

Generate flashcards as a JSON array:"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=settings.default_model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational flashcards."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            flashcards = json.loads(content)
            
            return flashcards
            
        except Exception as e:
            print(f"Error generating flashcards: {str(e)}")
            return []
    
    async def generate_quiz(
        self,
        topic: str,
        difficulty: str = "intermediate",
        count: int = 10,
        question_types: List[str] = None
    ) -> Dict[str, Any]:
        """Generate a quiz on a specific topic."""
        
        if question_types is None:
            question_types = ["multiple_choice", "true_false", "short_answer"]
        
        prompt = f"""Create a {count}-question quiz on the topic: {topic}

REQUIREMENTS:
- Difficulty level: {difficulty}
- Include these question types: {', '.join(question_types)}
- Provide correct answers and explanations
- Format as JSON with quiz metadata and questions array

Format:
{{
    "title": "Quiz Title",
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "questions": [
        {{
            "type": "multiple_choice",
            "question": "Question text",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Why this is correct"
        }}
    ]
}}"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=settings.default_model,
                messages=[
                    {"role": "system", "content": "You are an expert quiz creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            quiz_data = json.loads(content)
            
            return quiz_data
            
        except Exception as e:
            print(f"Error generating quiz: {str(e)}")
            return {
                "title": f"Quiz on {topic}",
                "topic": topic,
                "difficulty": difficulty,
                "questions": []
            }