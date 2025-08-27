from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
from app.api.auth.auth import router as auth_router
from app.api.documents.documents import router as documents_router
from app.api.tutor.tutor import router as tutor_router
from app.api.progress.progress import router as progress_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Global Brain Student Edition API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    
    yield
    
    # Shutdown
    print("Shutting down Global Brain Student Edition API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Your AI study partner that organizes notes, tutors you at your level, and tracks progress — in minutes a day.",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Include routers
app.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/v1/docs", tags=["Documents"])
app.include_router(tutor_router, prefix="/v1/tutor", tags=["Tutor"])
app.include_router(progress_router, prefix="/v1/progress", tags=["Progress"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Global Brain Student Edition API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return {
        "detail": "Endpoint not found",
        "error_code": "NOT_FOUND",
        "available_endpoints": [
            "/v1/auth/signup",
            "/v1/auth/login",
            "/v1/docs/upload",
            "/v1/tutor/chat",
            "/v1/tutor/boost/start",
            "/v1/progress/overview"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )