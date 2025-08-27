from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    s3_uri = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Document metadata
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    
    # Tags and organization
    tags = Column(Text, nullable=True)  # JSON string of tags
    topic = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
    course = relationship("Course", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")
    flashcards = relationship("Flashcard", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', status='{self.status}')>"

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    
    # Chunk metadata
    chunk_hash = Column(String(64), nullable=False)  # For deduplication
    chunk_type = Column(String(50), default="text")  # text, table, image, etc.
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    embeddings = relationship("Embedding", back_populates="chunk")
    flashcards = relationship("Flashcard", back_populates="chunk")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, idx={self.chunk_index})>"

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, sentence-transformers, etc.
    model_name = Column(String(100), nullable=False)
    vector_ref = Column(String(255), nullable=False)  # Reference to vector in vector DB
    embedding_dimension = Column(Integer, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    chunk = relationship("DocumentChunk", back_populates="embeddings")

    def __repr__(self):
        return f"<Embedding(id={self.id}, chunk_id={self.chunk_id}, provider='{self.provider}')>"