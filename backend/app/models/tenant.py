from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    plan = Column(String, default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())