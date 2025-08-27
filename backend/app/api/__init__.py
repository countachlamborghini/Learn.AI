"""API routes module."""

from fastapi import APIRouter
from .auth import router as auth_router
from .documents import router as documents_router
from .tutor import router as tutor_router
from .progress import router as progress_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(documents_router, prefix="/docs", tags=["documents"])
api_router.include_router(tutor_router, prefix="/tutor", tags=["tutor"])
api_router.include_router(progress_router, prefix="/progress", tags=["progress"])