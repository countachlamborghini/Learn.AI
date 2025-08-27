"""RAG (Retrieval Augmented Generation) service."""

import json
import hashlib
from typing import List, Dict, Any, Optional
import openai
from sentence_transformers import SentenceTransformer
import pinecone
from sqlalchemy.orm import Session

from ..models.document import DocumentChunk, Embedding
from ..models.user import User
from ..config import settings


class RAGService:
    """Service for RAG operations."""
    
    def __init__(self):
        # Initialize OpenAI
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        
        # Initialize Pinecone
        if settings.pinecone_api_key:
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            self.index = pinecone.Index(settings.pinecone_index_name)
        else:
            self.index = None
        
        # Initialize local embedding model as fallback
        self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def generate_embeddings_for_document(self, document_id: int, db: Session):
        """Generate embeddings for all chunks of a document."""
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).all()
        
        for chunk in chunks:
            await self._generate_chunk_embedding(chunk, db)
    
    async def _generate_chunk_embedding(self, chunk: DocumentChunk, db: Session):
        """Generate embedding for a single chunk."""
        try:
            # Try OpenAI first
            if settings.openai_api_key:
                embedding_vector = await self._get_openai_embedding(chunk.text)
                provider = "openai"
                model_name = "text-embedding-3-small"
            else:
                # Fallback to local model
                embedding_vector = self.local_model.encode(chunk.text).tolist()
                provider = "sentence-transformers"
                model_name = "all-MiniLM-L6-v2"
            
            # Store in Pinecone if available
            vector_id = None
            if self.index:
                vector_id = f"chunk_{chunk.id}"
                metadata = {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.id,
                    "user_id": chunk.document.user_id,
                    "tenant_id": chunk.document.user.tenant_id if chunk.document.user.tenant_id else 0,
                    "text": chunk.text[:1000],  # Truncate for metadata
                    "section_title": chunk.section_title,
                    "page_number": chunk.page_number
                }
                
                self.index.upsert(
                    vectors=[(vector_id, embedding_vector, metadata)]
                )
            
            # Create embedding record
            embedding_hash = hashlib.md5(
                json.dumps(embedding_vector, sort_keys=True).encode()
            ).hexdigest()
            
            embedding = Embedding(
                chunk_id=chunk.id,
                provider=provider,
                model_name=model_name,
                vector_id=vector_id,
                embedding_hash=embedding_hash
            )
            
            db.add(embedding)
            
        except Exception as e:
            print(f"Error generating embedding for chunk {chunk.id}: {str(e)}")
    
    async def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI."""
        response = await openai.Embedding.acreate(
            model="text-embedding-3-small",
            input=text
        )
        return response['data'][0]['embedding']
    
    async def search_documents(
        self, 
        query: str, 
        user: User,
        top_k: int = 10,
        course_id: Optional[int] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Search documents using vector similarity."""
        
        # Generate query embedding
        if settings.openai_api_key:
            query_embedding = await self._get_openai_embedding(query)
        else:
            query_embedding = self.local_model.encode(query).tolist()
        
        # Build filter for user/tenant isolation
        filter_dict = {
            "user_id": user.id
        }
        if user.tenant_id:
            filter_dict["tenant_id"] = user.tenant_id
        
        if course_id:
            filter_dict["course_id"] = course_id
        
        # Search in Pinecone
        if self.index:
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k * 2,  # Get more for re-ranking
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            results = []
            for match in search_results['matches']:
                chunk_id = match['metadata']['chunk_id']
                chunk = db.query(DocumentChunk).filter(
                    DocumentChunk.id == chunk_id
                ).first()
                
                if chunk:
                    results.append({
                        'chunk_id': chunk.id,
                        'document_id': chunk.document_id,
                        'document_name': chunk.document.original_filename,
                        'text': chunk.text,
                        'section_title': chunk.section_title,
                        'page_number': chunk.page_number,
                        'score': match['score'],
                        'metadata': match['metadata']
                    })
            
            # Re-rank using cross-encoder (simplified - would use actual re-ranker)
            results = await self._rerank_results(query, results)
            
            return results[:top_k]
        
        else:
            # Fallback to database search (less efficient)
            return await self._fallback_search(query, user, top_k, course_id, db)
    
    async def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Re-rank search results (simplified implementation)."""
        # In production, you'd use a cross-encoder model like bge-reranker-large
        # For now, just return results sorted by score
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    async def _fallback_search(
        self, 
        query: str, 
        user: User, 
        top_k: int, 
        course_id: Optional[int],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Fallback search using database full-text search."""
        # Simple keyword search
        query_filter = DocumentChunk.text.ilike(f"%{query}%")
        
        chunks = db.query(DocumentChunk).join(DocumentChunk.document).filter(
            query_filter,
            DocumentChunk.document.has(user_id=user.id)
        ).limit(top_k).all()
        
        results = []
        for chunk in chunks:
            results.append({
                'chunk_id': chunk.id,
                'document_id': chunk.document_id,
                'document_name': chunk.document.original_filename,
                'text': chunk.text,
                'section_title': chunk.section_title,
                'page_number': chunk.page_number,
                'score': 0.5,  # Default score
                'metadata': {}
            })
        
        return results
    
    def get_chunk_context(self, chunk_id: int, db: Session) -> Dict[str, Any]:
        """Get context around a specific chunk."""
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            return {}
        
        # Get surrounding chunks
        prev_chunk = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == chunk.document_id,
            DocumentChunk.chunk_index == chunk.chunk_index - 1
        ).first()
        
        next_chunk = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == chunk.document_id,
            DocumentChunk.chunk_index == chunk.chunk_index + 1
        ).first()
        
        return {
            'current': chunk.text,
            'previous': prev_chunk.text if prev_chunk else None,
            'next': next_chunk.text if next_chunk else None,
            'document_name': chunk.document.original_filename,
            'section_title': chunk.section_title,
            'page_number': chunk.page_number
        }