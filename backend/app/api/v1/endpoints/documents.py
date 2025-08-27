from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import uuid
import boto3
from datetime import datetime

from app.core.database import get_db
from app.core.auth.jwt import get_current_user
from app.core.config import settings
from app.schemas.document import DocumentResponse, DocumentUpload, DocumentWithChunksResponse
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    course_id: Optional[int] = Form(None),
    topic: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for processing."""
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed"
        )
    
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large"
        )
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Upload to S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    s3_uri = f"s3://{settings.S3_BUCKET_NAME}/{current_user.id}/{unique_filename}"
    
    try:
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            f"{current_user.id}/{unique_filename}",
            ExtraArgs={'ContentType': file.content_type}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage"
        )
    
    # Create document record
    document = Document(
        user_id=current_user.id,
        course_id=course_id,
        title=title,
        filename=unique_filename,
        s3_uri=s3_uri,
        mime_type=file.content_type,
        file_size=file.size,
        status="uploaded",
        topic=topic,
        tags=tags
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Start async processing
    try:
        processor = DocumentProcessor()
        processor.process_document_async(document.id)
    except Exception as e:
        # Update document status to failed
        document.status = "failed"
        document.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start document processing"
        )
    
    return DocumentResponse.from_orm(document)

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for the current user."""
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.created_at.desc()).all()
    
    return [DocumentResponse.from_orm(doc) for doc in documents]

@router.get("/{document_id}", response_model=DocumentWithChunksResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document with its chunks."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get chunks
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_index).all()
    
    response = DocumentWithChunksResponse.from_orm(document)
    response.chunks = [DocumentChunkResponse.from_orm(chunk) for chunk in chunks]
    
    return response

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document and its associated data."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete from S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        s3_key = document.s3_uri.replace(f"s3://{settings.S3_BUCKET_NAME}/", "")
        s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
    except Exception as e:
        # Log error but continue with deletion
        pass
    
    # Delete from vector store
    try:
        vector_store = VectorStore()
        vector_store.delete_document_embeddings(document_id)
    except Exception as e:
        # Log error but continue with deletion
        pass
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}

@router.post("/{document_id}/reindex")
async def reindex_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reindex a document (admin/owner only)."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update status and start reindexing
    document.status = "processing"
    document.processing_started_at = datetime.utcnow()
    db.commit()
    
    try:
        processor = DocumentProcessor()
        processor.process_document_async(document_id)
    except Exception as e:
        document.status = "failed"
        document.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start reindexing"
        )
    
    return {"message": "Document reindexing started"}