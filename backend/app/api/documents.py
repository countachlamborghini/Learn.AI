"""Documents API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..auth import get_current_active_user
from ..models.user import User
from ..models.document import Document, DocumentChunk
from ..services.document_service import DocumentService
from ..services.llm_service import LLMService

router = APIRouter()
document_service = DocumentService()
llm_service = LLMService()


class DocumentResponse(BaseModel):
    """Document response schema."""
    id: int
    filename: str
    original_filename: str
    status: str
    file_size: int
    total_tokens: int
    total_chunks: int
    created_at: str
    
    class Config:
        from_attributes = True


class FlashcardResponse(BaseModel):
    """Flashcard response schema."""
    id: int
    front: str
    back: str
    difficulty: str
    topic: Optional[str]


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    course_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a document for processing."""
    
    # Read file content
    content = await file.read()
    
    try:
        document = await document_service.upload_document(
            file_content=content,
            filename=file.filename,
            user=current_user,
            course_id=course_id,
            db=db
        )
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            status=document.status,
            file_size=document.file_size,
            total_tokens=document.total_tokens,
            total_chunks=document.total_chunks,
            created_at=document.created_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user."""
    documents = document_service.get_user_documents(current_user.id, db)
    
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            original_filename=doc.original_filename,
            status=doc.status,
            file_size=doc.file_size,
            total_tokens=doc.total_tokens,
            total_chunks=doc.total_chunks,
            created_at=doc.created_at.isoformat()
        )
        for doc in documents
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document."""
    document = document_service.get_document(document_id, current_user.id, db)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        original_filename=document.original_filename,
        status=document.status,
        file_size=document.file_size,
        total_tokens=document.total_tokens,
        total_chunks=document.total_chunks,
        created_at=document.created_at.isoformat()
    )


@router.get("/{document_id}/flashcards", response_model=List[FlashcardResponse])
async def get_document_flashcards(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get flashcards for a document."""
    document = document_service.get_document(document_id, current_user.id, db)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    flashcards = db.query(Document).filter(Document.id == document_id).first().flashcards
    
    return [
        FlashcardResponse(
            id=card.id,
            front=card.front,
            back=card.back,
            difficulty=card.difficulty,
            topic=card.topic
        )
        for card in flashcards
    ]


@router.post("/{document_id}/generate-flashcards")
async def generate_flashcards_for_document(
    document_id: int,
    count: int = 10,
    reading_level: str = "high_school",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate flashcards for a document."""
    document = document_service.get_document(document_id, current_user.id, db)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != "completed":
        raise HTTPException(status_code=400, detail="Document is still processing")
    
    # Get document chunks
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).all()
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No content available for flashcard generation")
    
    # Combine chunk texts
    full_text = "\n\n".join([chunk.text for chunk in chunks[:5]])  # Limit to first 5 chunks
    
    # Generate flashcards
    flashcards_data = await llm_service.generate_flashcards(
        text=full_text,
        reading_level=reading_level,
        count=count
    )
    
    # Save flashcards to database
    from ..models.learning import Flashcard
    
    saved_flashcards = []
    for card_data in flashcards_data:
        flashcard = Flashcard(
            document_id=document_id,
            front=card_data['front'],
            back=card_data['back'],
            difficulty=reading_level
        )
        db.add(flashcard)
        saved_flashcards.append(flashcard)
    
    db.commit()
    
    return {
        "message": f"Generated {len(saved_flashcards)} flashcards",
        "flashcards": [
            {
                "id": card.id,
                "front": card.front,
                "back": card.back
            }
            for card in saved_flashcards
        ]
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = document_service.get_document(document_id, current_user.id, db)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from database (cascades to chunks and embeddings)
    db.delete(document)
    db.commit()
    
    # TODO: Delete from S3 and Pinecone
    
    return {"message": "Document deleted successfully"}