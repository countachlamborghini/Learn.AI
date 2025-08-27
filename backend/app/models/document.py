from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    s3_uri = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    token_count = Column(Integer, nullable=True)
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
    course = relationship("Course", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")
    flashcards = relationship("Flashcard", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "doc_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    chunk_hash = Column(String, nullable=False)
    section_title = Column(String, nullable=True)
    page_number = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    embeddings = relationship("Embedding", back_populates="chunk")
    flashcards = relationship("Flashcard", back_populates="chunk")


class Embedding(Base):
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("doc_chunks.id"), nullable=False)
    provider = Column(String, default="openai")  # openai, local
    model_name = Column(String, nullable=False)
    vector_ref = Column(String, nullable=False)  # Reference to vector in ChromaDB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chunk = relationship("DocumentChunk", back_populates="embeddings")


class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    chunk_id = Column(Integer, ForeignKey("doc_chunks.id"), nullable=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    difficulty = Column(String, default="medium")  # easy, medium, hard
    tags = Column(Text, nullable=True)  # JSON array of tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="flashcards")
    chunk = relationship("DocumentChunk", back_populates="flashcards")