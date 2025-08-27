"""Billing and subscription models."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class BillingCustomer(Base):
    """Billing customer model."""
    __tablename__ = "billing_customers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    stripe_customer_id = Column(String, unique=True)
    stripe_subscription_id = Column(String)
    plan = Column(String, default="free")  # free, pro, school
    status = Column(String, default="active")  # active, inactive, cancelled
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Usage tracking
    monthly_documents_used = Column(Integer, default=0)
    monthly_flashcards_used = Column(Integer, default=0)
    monthly_messages_used = Column(Integer, default=0)
    monthly_brain_boosts_used = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User")
    tenant = relationship("Tenant")