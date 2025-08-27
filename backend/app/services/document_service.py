"""Document processing and ingestion service."""

import os
import hashlib
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
import aiofiles
import boto3
from sqlalchemy.orm import Session
import PyPDF2
from docx import Document as DocxDocument
from pptx import Presentation
from PIL import Image
import pytesseract

from ..models.document import Document, DocumentChunk, DocumentStatus
from ..models.user import User
from ..config import settings
from .rag_service import RAGService


class DocumentService:
    """Service for document processing and management."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.rag_service = RAGService()
    
    async def upload_document(
        self, 
        file_content: bytes, 
        filename: str, 
        user: User,
        course_id: Optional[int] = None,
        db: Session = None
    ) -> Document:
        """Upload and process a document."""
        
        # Validate file type
        file_ext = Path(filename).suffix.lower()
        if file_ext not in settings.allowed_file_types:
            raise ValueError(f"File type {file_ext} not allowed")
        
        # Validate file size
        if len(file_content) > settings.max_file_size:
            raise ValueError("File size exceeds maximum allowed size")
        
        # Generate unique filename
        file_hash = hashlib.md5(file_content).hexdigest()
        unique_filename = f"{user.id}/{file_hash}_{filename}"
        
        # Upload to S3
        s3_uri = await self._upload_to_s3(file_content, unique_filename)
        
        # Create document record
        document = Document(
            user_id=user.id,
            course_id=course_id,
            filename=unique_filename,
            original_filename=filename,
            s3_uri=s3_uri,
            mime_type=self._get_mime_type(file_ext),
            file_size=len(file_content),
            status=DocumentStatus.PROCESSING
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Process document asynchronously
        asyncio.create_task(self._process_document(document.id, file_content, db))
        
        return document
    
    async def _upload_to_s3(self, file_content: bytes, filename: str) -> str:
        """Upload file to S3."""
        try:
            self.s3_client.put_object(
                Bucket=settings.s3_bucket_name,
                Key=filename,
                Body=file_content
            )
            return f"s3://{settings.s3_bucket_name}/{filename}"
        except Exception as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
    
    async def _process_document(self, document_id: int, file_content: bytes, db: Session):
        """Process document content for RAG."""
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return
            
            # Extract text based on file type
            text_content = await self._extract_text(file_content, document.original_filename)
            
            # Chunk the text
            chunks = await self._chunk_text(text_content, document_id)
            
            # Save chunks to database
            total_tokens = 0
            for i, chunk_data in enumerate(chunks):
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=i,
                    text=chunk_data['text'],
                    token_count=chunk_data['token_count'],
                    chunk_hash=hashlib.md5(chunk_data['text'].encode()).hexdigest(),
                    section_title=chunk_data.get('section_title'),
                    page_number=chunk_data.get('page_number'),
                    metadata=chunk_data.get('metadata', {})
                )
                db.add(chunk)
                total_tokens += chunk_data['token_count']
            
            # Update document status
            document.status = DocumentStatus.COMPLETED
            document.total_tokens = total_tokens
            document.total_chunks = len(chunks)
            
            db.commit()
            
            # Generate embeddings for chunks
            await self.rag_service.generate_embeddings_for_document(document_id, db)
            
        except Exception as e:
            # Update document status to failed
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = DocumentStatus.FAILED
                document.metadata = {"error": str(e)}
                db.commit()
    
    async def _extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text from various file types."""
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            return await self._extract_pdf_text(file_content)
        elif file_ext == '.docx':
            return await self._extract_docx_text(file_content)
        elif file_ext == '.pptx':
            return await self._extract_pptx_text(file_content)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            return await self._extract_image_text(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    async def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF."""
        import io
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    
    async def _extract_docx_text(self, file_content: bytes) -> str:
        """Extract text from DOCX."""
        import io
        doc_file = io.BytesIO(file_content)
        doc = DocxDocument(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text
    
    async def _extract_pptx_text(self, file_content: bytes) -> str:
        """Extract text from PPTX."""
        import io
        ppt_file = io.BytesIO(file_content)
        ppt = Presentation(ppt_file)
        
        text = ""
        for slide in ppt.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        
        return text
    
    async def _extract_image_text(self, file_content: bytes) -> str:
        """Extract text from image using OCR."""
        import io
        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image)
        return text
    
    async def _chunk_text(self, text: str, document_id: int) -> List[Dict[str, Any]]:
        """Chunk text into manageable pieces for RAG."""
        # Simple chunking strategy - can be improved with semantic chunking
        max_chunk_size = 1000  # tokens (approximate)
        overlap = 100  # token overlap between chunks
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for paragraph in paragraphs:
            # Approximate token count (4 chars = 1 token)
            paragraph_tokens = len(paragraph) // 4
            
            if current_tokens + paragraph_tokens > max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'text': current_chunk.strip(),
                    'token_count': current_tokens,
                    'metadata': {}
                })
                
                # Start new chunk with overlap
                if len(current_chunk) > overlap * 4:
                    current_chunk = current_chunk[-overlap * 4:] + "\n\n" + paragraph
                    current_tokens = overlap + paragraph_tokens
                else:
                    current_chunk = paragraph
                    current_tokens = paragraph_tokens
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
                current_tokens += paragraph_tokens
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'token_count': current_tokens,
                'metadata': {}
            })
        
        return chunks
    
    def _get_mime_type(self, file_ext: str) -> str:
        """Get MIME type for file extension."""
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return mime_types.get(file_ext, 'application/octet-stream')
    
    def get_user_documents(self, user_id: int, db: Session) -> List[Document]:
        """Get all documents for a user."""
        return db.query(Document).filter(Document.user_id == user_id).all()
    
    def get_document(self, document_id: int, user_id: int, db: Session) -> Optional[Document]:
        """Get a specific document for a user."""
        return db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()