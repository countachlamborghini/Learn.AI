import logging
import asyncio
from typing import List, Dict, Any
import boto3
import PyPDF2
import docx
import json
import hashlib
from datetime import datetime

from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document, DocumentChunk, Embedding
from app.services.vector_store import VectorStore
from app.services.ai_orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.vector_store = VectorStore()
        self.ai_orchestrator = AIOrchestrator()
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def process_document_async(self, document_id: int):
        """Start async document processing."""
        asyncio.create_task(self._process_document(document_id))
    
    async def _process_document(self, document_id: int):
        """Process a document asynchronously."""
        db = next(get_db())
        try:
            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document {document_id} not found")
                return
            
            # Update status to processing
            document.status = "processing"
            document.processing_started_at = datetime.utcnow()
            db.commit()
            
            # Download file from S3
            file_content = await self._download_from_s3(document.s3_uri)
            
            # Extract text based on file type
            text_content = await self._extract_text(file_content, document.mime_type)
            
            # Chunk the text
            chunks = await self._chunk_text(text_content, document.id)
            
            # Create embeddings and store in vector database
            await self._create_embeddings(chunks, document)
            
            # Generate summary
            summary = await self._generate_summary(text_content)
            
            # Generate flashcards
            await self._generate_flashcards(chunks, document.id)
            
            # Update document status
            document.status = "completed"
            document.processing_completed_at = datetime.utcnow()
            document.summary = summary
            document.token_count = len(text_content.split())  # Rough estimate
            document.word_count = len(text_content.split())
            db.commit()
            
            logger.info(f"Document {document_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            document.status = "failed"
            document.error_message = str(e)
            db.commit()
    
    async def _download_from_s3(self, s3_uri: str) -> bytes:
        """Download file from S3."""
        try:
            bucket = settings.S3_BUCKET_NAME
            key = s3_uri.replace(f"s3://{bucket}/", "")
            
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
            
        except Exception as e:
            logger.error(f"Error downloading from S3: {e}")
            raise
    
    async def _extract_text(self, file_content: bytes, mime_type: str) -> str:
        """Extract text from different file types."""
        try:
            if mime_type == "application/pdf":
                return await self._extract_pdf_text(file_content)
            elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return await self._extract_docx_text(file_content)
            elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                return await self._extract_pptx_text(file_content)
            elif mime_type in ["image/jpeg", "image/png"]:
                return await self._extract_image_text(file_content)
            else:
                return file_content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    async def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF."""
        try:
            pdf_reader = PyPDF2.PdfReader(file_content)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    async def _extract_docx_text(self, file_content: bytes) -> str:
        """Extract text from DOCX."""
        try:
            doc = docx.Document(file_content)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return ""
    
    async def _extract_pptx_text(self, file_content: bytes) -> str:
        """Extract text from PPTX."""
        try:
            # This would require python-pptx library
            # For now, return placeholder
            return "PPTX text extraction not implemented yet"
        except Exception as e:
            logger.error(f"Error extracting PPTX text: {e}")
            return ""
    
    async def _extract_image_text(self, file_content: bytes) -> str:
        """Extract text from image using OCR."""
        try:
            # This would require pytesseract and PIL
            # For now, return placeholder
            return "Image OCR not implemented yet"
        except Exception as e:
            logger.error(f"Error extracting image text: {e}")
            return ""
    
    async def _chunk_text(self, text: str, document_id: int) -> List[Dict[str, Any]]:
        """Chunk text into smaller pieces."""
        try:
            # Simple chunking by paragraphs
            paragraphs = text.split('\n\n')
            chunks = []
            
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) < 50:  # Skip very short paragraphs
                    continue
                
                # Create chunk hash for deduplication
                chunk_hash = hashlib.md5(paragraph.encode()).hexdigest()
                
                chunks.append({
                    "chunk_index": i,
                    "text": paragraph.strip(),
                    "token_count": len(paragraph.split()),
                    "chunk_hash": chunk_hash,
                    "document_id": document_id
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise
    
    async def _create_embeddings(self, chunks: List[Dict[str, Any]], document: Document):
        """Create embeddings for chunks and store in vector database."""
        db = next(get_db())
        try:
            for chunk_data in chunks:
                # Save chunk to database
                chunk = DocumentChunk(
                    document_id=chunk_data["document_id"],
                    chunk_index=chunk_data["chunk_index"],
                    text=chunk_data["text"],
                    token_count=chunk_data["token_count"],
                    chunk_hash=chunk_data["chunk_hash"]
                )
                db.add(chunk)
                db.commit()
                db.refresh(chunk)
                
                # Create embedding
                metadata = {
                    "user_id": document.user_id,
                    "tenant_id": document.user_id,  # Simplified for MVP
                    "document_id": document.id,
                    "document_title": document.title,
                    "chunk_index": chunk.chunk_index
                }
                
                vector_id = await self.vector_store.store_chunk_embedding(
                    chunk_id=chunk.id,
                    text=chunk.text,
                    metadata=metadata
                )
                
                # Save embedding reference
                embedding = Embedding(
                    chunk_id=chunk.id,
                    provider="openai",
                    model_name=settings.EMBEDDING_MODEL,
                    vector_ref=vector_id,
                    embedding_dimension=1536
                )
                db.add(embedding)
                db.commit()
                
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    async def _generate_summary(self, text: str) -> str:
        """Generate a summary of the document."""
        try:
            # Use AI orchestrator to generate summary
            summary = await self.ai_orchestrator.generate_summary(text, max_length=300)
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary generation failed"
    
    async def _generate_flashcards(self, chunks: List[Dict[str, Any]], document_id: int):
        """Generate flashcards from document chunks."""
        db = next(get_db())
        try:
            # Generate flashcards from first few chunks
            for chunk_data in chunks[:3]:  # Limit to first 3 chunks for performance
                flashcards = await self.ai_orchestrator.generate_flashcards(
                    text=chunk_data["text"],
                    level="medium",
                    count=3
                )
                
                # Save flashcards to database
                for flashcard_data in flashcards:
                    flashcard = Flashcard(
                        document_id=document_id,
                        front=flashcard_data["front"],
                        back=flashcard_data["back"],
                        difficulty="medium"
                    )
                    db.add(flashcard)
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            # Don't fail the entire process for flashcard generation
            pass