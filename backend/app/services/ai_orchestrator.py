import openai
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.services.vector_store import VectorStore
from app.services.tools import (
    search_docs,
    get_chunks,
    make_flashcards,
    make_quiz,
    micro_lesson,
    math_solver,
    grade_answer,
    level_adapter
)

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.vector_store = VectorStore()
        
        # Available tools for function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_docs",
                    "description": "Search documents for relevant information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "filters": {"type": "object", "description": "Search filters"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_chunks",
                    "description": "Get full text of document chunks",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chunk_ids": {"type": "array", "items": {"type": "integer"}}
                        },
                        "required": ["chunk_ids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "make_flashcards",
                    "description": "Generate flashcards from text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to create flashcards from"},
                            "level": {"type": "string", "description": "Difficulty level"},
                            "count": {"type": "integer", "description": "Number of flashcards to create"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "make_quiz",
                    "description": "Generate quiz questions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {"type": "string", "description": "Topic scope"},
                            "count": {"type": "integer", "description": "Number of questions"},
                            "level": {"type": "string", "description": "Difficulty level"}
                        },
                        "required": ["scope", "count"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "math_solver",
                    "description": "Solve mathematical expressions with steps",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "Mathematical expression"},
                            "show_steps": {"type": "boolean", "description": "Show solution steps"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "level_adapter",
                    "description": "Adapt text to different reading levels",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to adapt"},
                            "target_level": {"type": "string", "description": "Target reading level"}
                        },
                        "required": ["text", "target_level"]
                    }
                }
            }
        ]
        
        self.system_prompt = """You are Global Brain — a study companion designed to help students learn effectively. 

Core Principles:
1. Always cite sources when providing information
2. Show steps for STEM problems when asked or when solving
3. Adapt your language to the student's reading level
4. Ask clarifying questions only when essential
5. Never invent citations or sources
6. Avoid unsafe content and direct to help when needed
7. Be encouraging and supportive while maintaining academic rigor

When answering questions:
- Use the search_docs tool to find relevant information
- Provide clear, structured responses
- Include step-by-step explanations for complex topics
- Adapt your language to the specified level (kid, HS, AP, college)
- Always cite your sources with [DocumentName §Section] format

For math and science:
- Use the math_solver tool for calculations
- Show all steps clearly
- Explain the reasoning behind each step

Remember: You're here to help students learn, not just provide answers."""

    async def answer_question(
        self,
        user_id: int,
        tenant_id: int,
        query: str,
        level: str = "medium",
        scope: Optional[str] = None,
        session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Answer a student's question using RAG and tool calling."""
        try:
            # Rewrite query for better retrieval
            rewritten_query = await self._rewrite_query(query)
            
            # Search for relevant documents
            search_results = await search_docs(rewritten_query, {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "scope": scope
            })
            
            if not search_results:
                return {
                    "answer": "I don't have enough information to answer that question. Try uploading some relevant documents first!",
                    "sources": [],
                    "tokens_used": 0,
                    "model_used": settings.OPENAI_MODEL
                }
            
            # Get full text of top chunks
            chunk_ids = [result["chunk_id"] for result in search_results[:8]]
            chunks = await get_chunks(chunk_ids)
            
            # Build context
            context = "\n\n".join([chunk["text"] for chunk in chunks])
            
            # Create messages for the conversation
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Question: {query}\n\nContext: {context}\n\nPlease answer at a {level} level."}
            ]
            
            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=1000,
                temperature=0.7
            )
            
            # Process tool calls if any
            final_answer = response.choices[0].message.content or ""
            tool_calls = response.choices[0].message.tool_calls or []
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Execute tool
                tool_result = await self._execute_tool(tool_name, tool_args)
                
                # Add tool result to conversation
                messages.append(response.choices[0].message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })
                
                # Get final answer
                final_response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7
                )
                
                final_answer = final_response.choices[0].message.content or ""
            
            # Format sources
            sources = []
            for result in search_results[:5]:
                sources.append({
                    "document_title": result.get("document_title", "Unknown"),
                    "section": result.get("section_title", "Unknown"),
                    "chunk_id": result["chunk_id"],
                    "relevance_score": result.get("score", 0)
                })
            
            return {
                "answer": final_answer,
                "sources": sources,
                "tokens_used": response.usage.total_tokens,
                "model_used": settings.OPENAI_MODEL
            }
            
        except Exception as e:
            logger.error(f"Error in answer_question: {e}")
            return {
                "answer": "I'm sorry, I encountered an error while processing your question. Please try again.",
                "sources": [],
                "tokens_used": 0,
                "model_used": settings.OPENAI_MODEL
            }

    async def _rewrite_query(self, query: str) -> str:
        """Rewrite query to improve retrieval."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Rewrite the user's question to improve document retrieval. Focus on key concepts and terms."},
                    {"role": "user", "content": query}
                ],
                max_tokens=100,
                temperature=0.3
            )
            return response.choices[0].message.content or query
        except:
            return query

    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool function."""
        tool_functions = {
            "search_docs": search_docs,
            "get_chunks": get_chunks,
            "make_flashcards": make_flashcards,
            "make_quiz": make_quiz,
            "micro_lesson": micro_lesson,
            "math_solver": math_solver,
            "grade_answer": grade_answer,
            "level_adapter": level_adapter
        }
        
        if tool_name in tool_functions:
            return await tool_functions[tool_name](**args)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    async def generate_flashcards(
        self,
        text: str,
        level: str = "medium",
        count: int = 5
    ) -> List[Dict[str, str]]:
        """Generate flashcards from text."""
        try:
            prompt = f"""Create {count} high-quality flashcards from this text at a {level} level.

Text: {text}

Create flashcards in this format:
1. Front: [Question]
   Back: [Answer]

2. Front: [Question]
   Back: [Answer]

... and so on.

Make sure the questions are clear and the answers are concise but complete."""

            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            # Parse the response to extract flashcards
            content = response.choices[0].message.content
            flashcards = self._parse_flashcards(content)
            
            return flashcards[:count]
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return []

    def _parse_flashcards(self, content: str) -> List[Dict[str, str]]:
        """Parse flashcards from AI response."""
        flashcards = []
        lines = content.split('\n')
        
        current_front = None
        for line in lines:
            line = line.strip()
            if line.startswith('Front:'):
                current_front = line.replace('Front:', '').strip()
            elif line.startswith('Back:') and current_front:
                back = line.replace('Back:', '').strip()
                flashcards.append({
                    "front": current_front,
                    "back": back
                })
                current_front = None
        
        return flashcards

    async def generate_quiz(
        self,
        scope: str,
        count: int = 5,
        level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions."""
        try:
            prompt = f"""Create {count} quiz questions about {scope} at a {level} level.

Create questions in this format:
1. Question: [Question text]
   Type: multiple_choice
   Options: [A, B, C, D]
   Answer: [Correct answer]
   Explanation: [Brief explanation]

2. Question: [Question text]
   Type: true_false
   Answer: [True/False]
   Explanation: [Brief explanation]

Make sure questions are clear and explanations are helpful."""

            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            questions = self._parse_quiz_questions(content)
            
            return questions[:count]
            
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return []

    def _parse_quiz_questions(self, content: str) -> List[Dict[str, Any]]:
        """Parse quiz questions from AI response."""
        questions = []
        # Implementation would parse the AI response into structured questions
        # This is a simplified version
        return questions