from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for magic link auth
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(String(50), default="student")  # student, teacher, admin
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Profile fields
    grade_level = Column(String(50), nullable=True)  # 9th, 10th, college, etc.
    subjects = Column(Text, nullable=True)  # JSON string of subjects
    timezone = Column(String(50), default="UTC")
    preferences = Column(Text, nullable=True)  # JSON string of user preferences
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    enrollments = relationship("Enrollment", back_populates="user")
    documents = relationship("Document", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    masteries = relationship("Mastery", back_populates="user")
    consents = relationship("Consent", back_populates="user")
    billing_customer = relationship("BillingCustomer", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"