from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Consent details
    consent_type = Column(String(100), nullable=False)  # data_processing, marketing, analytics, etc.
    data_use_scope = Column(Text, nullable=True)  # JSON string describing data use
    version = Column(String(20), nullable=False)  # Version of consent terms
    
    # Consent status
    granted = Column(Boolean, default=False)
    granted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Legal compliance
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    consent_method = Column(String(50), nullable=True)  # web, mobile, email
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="consents")

    def __repr__(self):
        return f"<Consent(id={self.id}, user_id={self.user_id}, type='{self.consent_type}', granted={self.granted})>"