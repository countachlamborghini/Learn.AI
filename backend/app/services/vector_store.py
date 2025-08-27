import pinecone
import openai
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from app.core.config import settings
from app.core.database import get_db
from app.models.document import DocumentChunk, Embedding

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        # Get or create index
        if settings.PINECONE_INDEX_NAME not in pinecone.list_indexes():
            pinecone.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=1536,  # OpenAI text-embedding-3-large dimension
                metric="cosine"
            )
        
        self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
        self.embedding_model = settings.EMBEDDING_MODEL
        
    async def create_embeddings(self, text: str) -> List[float]:
        """Create embeddings for text using OpenAI."""
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    async def store_chunk_embedding(
        self,
        chunk_id: int,
        text: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Store a chunk embedding in the vector database."""
        try:
            # Create embedding
            embedding = await self.create_embeddings(text)
            
            # Store in Pinecone
            vector_id = f"chunk_{chunk_id}"
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "text": text[:1000],  # Store first 1000 chars for context
                        **metadata
                    }
                }]
            )
            
            return vector_id
            
        except Exception as e:
            logger.error(f"Error storing chunk embedding: {e}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using semantic similarity."""
        try:
            # Create query embedding
            query_embedding = await self.create_embeddings(query)
            
            # Build filter string for Pinecone
            filter_string = None
            if filters:
                filter_parts = []
                for key, value in filters.items():
                    if isinstance(value, (int, str)):
                        filter_parts.append(f"{key} == {value}")
                    elif isinstance(value, list):
                        filter_parts.append(f"{key} in {value}")
                if filter_parts:
                    filter_string = " and ".join(filter_parts)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_string,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "chunk_id": match.metadata.get("chunk_id"),
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    async def delete_document_embeddings(self, document_id: int):
        """Delete all embeddings for a document."""
        try:
            # Get all chunk IDs for the document
            db = next(get_db())
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).all()
            
            # Delete from Pinecone
            vector_ids = [f"chunk_{chunk.id}" for chunk in chunks]
            if vector_ids:
                self.index.delete(ids=vector_ids)
            
            # Delete from database
            db.query(Embedding).filter(
                Embedding.chunk_id.in_([chunk.id for chunk in chunks])
            ).delete()
            db.commit()
            
        except Exception as e:
            logger.error(f"Error deleting document embeddings: {e}")
            raise
    
    async def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific chunk by ID."""
        try:
            db = next(get_db())
            chunk = db.query(DocumentChunk).filter(
                DocumentChunk.id == chunk_id
            ).first()
            
            if chunk:
                return {
                    "id": chunk.id,
                    "text": chunk.text,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "section_title": chunk.section_title,
                    "page_number": chunk.page_number
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting chunk by ID: {e}")
            return None
    
    async def get_chunks_by_ids(self, chunk_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple chunks by their IDs."""
        try:
            db = next(get_db())
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.id.in_(chunk_ids)
            ).all()
            
            return [{
                "id": chunk.id,
                "text": chunk.text,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "section_title": chunk.section_title,
                "page_number": chunk.page_number
            } for chunk in chunks]
            
        except Exception as e:
            logger.error(f"Error getting chunks by IDs: {e}")
            return []
    
    async def update_chunk_embedding(
        self,
        chunk_id: int,
        new_text: str,
        metadata: Dict[str, Any]
    ):
        """Update an existing chunk embedding."""
        try:
            # Create new embedding
            embedding = await self.create_embeddings(new_text)
            
            # Update in Pinecone
            vector_id = f"chunk_{chunk_id}"
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "text": new_text[:1000],
                        **metadata
                    }
                }]
            )
            
        except Exception as e:
            logger.error(f"Error updating chunk embedding: {e}")
            raise