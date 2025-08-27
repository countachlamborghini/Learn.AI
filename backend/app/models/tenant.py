from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=True)
    plan = Column(String(50), default="free")  # free, pro, school
    is_active = Column(Boolean, default=True)
    settings = Column(Text, nullable=True)  # JSON string of tenant settings
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # School-specific fields
    school_type = Column(String(50), nullable=True)  # elementary, high, college, etc.
    region = Column(String(100), nullable=True)
    compliance_settings = Column(Text, nullable=True)  # COPPA, FERPA settings
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    courses = relationship("Course", back_populates="tenant")
    billing_customer = relationship("BillingCustomer", back_populates="tenant", uselist=False)

    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', plan='{self.plan}')>"