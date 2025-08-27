from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class BillingCustomer(Base):
    __tablename__ = "billing_customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    
    # Stripe integration
    stripe_customer_id = Column(String(255), unique=True, nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Billing details
    plan = Column(String(50), default="free")  # free, pro, school
    status = Column(String(50), default="active")  # active, canceled, past_due, etc.
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    
    # Usage tracking
    documents_used = Column(Integer, default=0)
    messages_used = Column(Integer, default=0)
    brain_boosts_used = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="billing_customer")
    tenant = relationship("Tenant", back_populates="billing_customer")

    def __repr__(self):
        return f"<BillingCustomer(id={self.id}, plan='{self.plan}', status='{self.status}')>"