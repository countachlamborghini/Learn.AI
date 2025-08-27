from fastapi import APIRouter

from app.api.v1.endpoints import auth, documents, tutor, quiz, progress, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/docs", tags=["documents"])
api_router.include_router(tutor.router, prefix="/tutor", tags=["tutor"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])