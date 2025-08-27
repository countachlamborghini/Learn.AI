from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth.jwt import get_current_user, get_password_hash
from app.schemas.user import UserUpdate, UserResponse
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile."""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    try:
        # Update fields if provided
        if user_update.first_name is not None:
            current_user.first_name = user_update.first_name
        if user_update.last_name is not None:
            current_user.last_name = user_update.last_name
        if user_update.grade_level is not None:
            current_user.grade_level = user_update.grade_level
        if user_update.subjects is not None:
            current_user.subjects = user_update.subjects
        if user_update.timezone is not None:
            current_user.timezone = user_update.timezone
        if user_update.preferences is not None:
            current_user.preferences = user_update.preferences
        
        db.commit()
        db.refresh(current_user)
        
        return UserResponse.from_orm(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

@router.delete("/me")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account."""
    try:
        # Mark user as inactive instead of deleting
        current_user.is_active = False
        db.commit()
        
        return {"message": "Account deactivated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating account: {str(e)}"
        )