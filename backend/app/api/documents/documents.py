from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.document import Document, DocumentChunk, Flashcard
from app.services.document_service import DocumentService
from app.api.schemas import Document as DocumentSchema, DocumentChunk as DocumentChunkSchema, Flashcard as FlashcardSchema

router = APIRouter()


@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    course_id: int = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a document for processing"""
    try:
        document = await DocumentService.upload_document(
            file=file,
            user_id=current_user.id,
            title=title,
            course_id=course_id,
            db=db
        )
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[DocumentSchema])
async def list_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all documents for the current user"""
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/{document_id}/chunks", response_model=List[DocumentChunkSchema])
async def get_document_chunks(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chunks for a specific document"""
    # Verify document ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_index).all()
    
    return chunks


@router.get("/{document_id}/flashcards", response_model=List[FlashcardSchema])
async def get_document_flashcards(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get flashcards for a specific document"""
    # Verify document ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    flashcards = db.query(Flashcard).filter(
        Flashcard.document_id == document_id
    ).all()
    
    return flashcards


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # TODO: Delete from S3 and vector database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}