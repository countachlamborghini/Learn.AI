from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentCreate(BaseModel):
    title: str
    course_id: Optional[int] = None
    topic: Optional[str] = None
    tags: Optional[str] = None

class DocumentUpload(BaseModel):
    title: str
    course_id: Optional[int] = None
    topic: Optional[str] = None
    tags: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    mime_type: str
    file_size: int
    status: DocumentStatus
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    token_count: Optional[int] = None
    summary: Optional[str] = None
    topic: Optional[str] = None
    tags: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentChunkResponse(BaseModel):
    id: int
    chunk_index: int
    text: str
    token_count: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentWithChunksResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []