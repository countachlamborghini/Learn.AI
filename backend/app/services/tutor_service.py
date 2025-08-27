import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.document import DocumentChunk, Embedding
from app.models.tutor import Session as TutorSession, Message
from app.core.config import settings
import openai
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize embedding model for similarity search
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize OpenAI client
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key


class TutorService:
    
    @staticmethod
    async def chat_with_tutor(
        user_id: int,
        message: str,
        session_id: Optional[int],
        level: str = "high_school",
        scope: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Handle tutor chat interaction"""
        
        # Create or get session
        if session_id:
            session = db.query(TutorSession).filter(
                TutorSession.id == session_id,
                TutorSession.user_id == user_id
            ).first()
        else:
            session = TutorSession(
                user_id=user_id,
                session_type="tutor_chat",
                title=message[:50] + "..." if len(message) > 50 else message
            )
            db.add(session)
            db.flush()
        
        # Save user message
        user_message = Message(
            session_id=session.id,
            role="user",
            content=message
        )
        db.add(user_message)
        db.flush()
        
        # Retrieve relevant context
        context_chunks = await TutorService.retrieve_context(
            user_id=user_id,
            query=message,
            scope=scope,
            db=db
        )
        
        # Generate response
        response = await TutorService.generate_response(
            message=message,
            context_chunks=context_chunks,
            level=level,
            session_id=session.id,
            db=db
        )
        
        # Save assistant message
        assistant_message = Message(
            session_id=session.id,
            role="assistant",
            content=response["reply"],
            sources=response["sources"],
            tokens_in=response.get("tokens_in"),
            tokens_out=response.get("tokens_out"),
            model_used=response.get("model_used")
        )
        db.add(assistant_message)
        db.commit()
        
        return {
            "reply": response["reply"],
            "citations": response["citations"],
            "session_id": session.id,
            "sources": response["sources"]
        }
    
    @staticmethod
    async def retrieve_context(
        user_id: int,
        query: str,
        scope: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context using RAG"""
        
        # Generate query embedding
        query_embedding = embedding_model.encode(query)
        
        # Get user's document chunks
        chunks_query = db.query(DocumentChunk).join(
            DocumentChunk.document
        ).filter(
            DocumentChunk.document.has(user_id=user_id)
        )
        
        # Apply scope filters if provided
        if scope:
            if "document_ids" in scope:
                chunks_query = chunks_query.filter(
                    DocumentChunk.document_id.in_(scope["document_ids"])
                )
            if "course_ids" in scope:
                chunks_query = chunks_query.join(
                    DocumentChunk.document
                ).filter(
                    DocumentChunk.document.has(course_id=scope["course_ids"])
                )
        
        chunks = chunks_query.all()
        
        if not chunks:
            return []
        
        # Calculate similarities (simplified - in production use vector DB)
        similarities = []
        for chunk in chunks:
            chunk_embedding = embedding_model.encode(chunk.text)
            similarity = np.dot(query_embedding, chunk_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
            )
            similarities.append((similarity, chunk))
        
        # Sort by similarity and take top chunks
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_chunks = similarities[:8]  # Top 8 most relevant chunks
        
        return [
            {
                "chunk": chunk,
                "similarity": float(similarity),
                "source": {
                    "document_title": chunk.document.title,
                    "section_title": chunk.section_title,
                    "page_number": chunk.page_number
                }
            }
            for similarity, chunk in top_chunks
        ]
    
    @staticmethod
    async def generate_response(
        message: str,
        context_chunks: List[Dict[str, Any]],
        level: str,
        session_id: int,
        db: Session = None
    ) -> Dict[str, Any]:
        """Generate AI response using context"""
        
        if not settings.openai_api_key:
            # Fallback response when OpenAI is not available
            return {
                "reply": "I'm sorry, but I'm currently unable to provide AI-powered responses. Please check your OpenAI API configuration.",
                "sources": [],
                "citations": [],
                "tokens_in": 0,
                "tokens_out": 0,
                "model_used": "fallback"
            }
        
        # Build context from chunks
        context_text = ""
        sources = []
        
        for chunk_info in context_chunks:
            chunk = chunk_info["chunk"]
            context_text += f"\n\nSource: {chunk_info['source']['document_title']}"
            if chunk_info['source']['section_title']:
                context_text += f" - {chunk_info['source']['section_title']}"
            if chunk_info['source']['page_number']:
                context_text += f" (Page {chunk_info['source']['page_number']})"
            context_text += f"\n{chunk.text}"
            
            sources.append({
                "document_title": chunk_info['source']['document_title'],
                "section_title": chunk_info['source']['section_title'],
                "page_number": chunk_info['source']['page_number'],
                "similarity": chunk_info['similarity']
            })
        
        # Create system prompt based on level
        level_prompts = {
            "elementary": "You are a friendly tutor for elementary school students. Use simple language, short sentences, and lots of examples. Be encouraging and patient.",
            "middle": "You are a helpful tutor for middle school students. Use clear explanations and connect concepts to real-world examples.",
            "high_school": "You are an expert tutor for high school students. Provide detailed explanations with academic rigor while remaining accessible.",
            "college": "You are a university-level tutor. Provide comprehensive, scholarly explanations with appropriate depth and complexity."
        }
        
        system_prompt = level_prompts.get(level, level_prompts["high_school"])
        
        # Build the full prompt
        prompt = f"""You are Global Brain — a study companion. Always: 1) cite sources, 2) show steps for STEM when asked or when solving, 3) adapt reading level, 4) ask a brief clarifying question only if essential, 5) never invent citations, 6) avoid unsafe content and direct to help when needed.

{system_prompt}

Context from the student's documents:
{context_text}

Student question: {message}

Please provide a helpful, accurate response based on the context provided. If the context doesn't contain enough information to answer the question, say so clearly. Always cite your sources using the format [DocumentName §Section]."""
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content
            
            # Extract citations from response
            citations = TutorService.extract_citations(reply, sources)
            
            return {
                "reply": reply,
                "sources": sources,
                "citations": citations,
                "tokens_in": response.usage.prompt_tokens,
                "tokens_out": response.usage.completion_tokens,
                "model_used": settings.openai_model
            }
            
        except Exception as e:
            return {
                "reply": f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again later.",
                "sources": [],
                "citations": [],
                "tokens_in": 0,
                "tokens_out": 0,
                "model_used": "error"
            }
    
    @staticmethod
    def extract_citations(text: str, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract citations from response text"""
        citations = []
        
        # Simple citation extraction - look for [DocumentName §Section] patterns
        import re
        citation_pattern = r'\[([^\]]+)\]'
        matches = re.findall(citation_pattern, text)
        
        for match in matches:
            # Try to match with available sources
            for source in sources:
                if source['document_title'] in match or source['section_title'] in match:
                    citations.append({
                        "text": match,
                        "document_title": source['document_title'],
                        "section_title": source['section_title'],
                        "page_number": source['page_number']
                    })
                    break
        
        return citations
    
    @staticmethod
    async def start_brain_boost(
        user_id: int,
        timebox: int = 10,
        db: Session = None
    ) -> Dict[str, Any]:
        """Start a Brain Boost session"""
        
        # Create session
        session = TutorSession(
            user_id=user_id,
            session_type="brain_boost",
            title=f"Brain Boost - {timebox} minutes"
        )
        db.add(session)
        db.flush()
        
        # Generate quiz items based on user's weak areas
        quiz_items = await TutorService.generate_brain_boost_items(
            user_id=user_id,
            timebox=timebox,
            db=db
        )
        
        return {
            "quiz_id": session.id,
            "items": quiz_items,
            "estimated_time": timebox
        }
    
    @staticmethod
    async def generate_brain_boost_items(
        user_id: int,
        timebox: int,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Generate quiz items for Brain Boost"""
        
        # For now, create simple quiz items from user's documents
        # In production, this would analyze weak areas and create targeted questions
        
        documents = db.query(DocumentChunk).join(
            DocumentChunk.document
        ).filter(
            DocumentChunk.document.has(user_id=user_id)
        ).limit(5).all()
        
        quiz_items = []
        for i, chunk in enumerate(documents):
            # Create a simple question from the chunk
            question = f"What is the main topic discussed in this section: '{chunk.text[:100]}...'?"
            answer = f"This section discusses {chunk.section_title or 'the main content'} from {chunk.document.title}."
            
            quiz_items.append({
                "id": i + 1,
                "item_type": "open_ended",
                "prompt": question,
                "correct_answer": answer,
                "explanation": "This question tests your understanding of the main concepts in your study materials.",
                "difficulty": "medium",
                "source_refs": [{
                    "document_title": chunk.document.title,
                    "section_title": chunk.section_title,
                    "page_number": chunk.page_number
                }]
            })
        
        return quiz_items