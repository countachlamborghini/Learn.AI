"""Authentication schemas."""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from ..models.user import UserRole


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[str] = None


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tenant_code: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRole
    is_active: bool
    tenant_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None