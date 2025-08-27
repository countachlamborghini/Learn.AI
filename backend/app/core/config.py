from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Global Brain Student Edition"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/globalbrain"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Vector Database
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "global-brain-embeddings"
    
    # AI/LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    # Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-west-2"
    S3_BUCKET_NAME: str = "global-brain-documents"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # Hosts
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "image/jpeg",
        "image/png",
        "text/plain"
    ]
    
    # Analytics
    SENTRY_DSN: Optional[str] = None
    
    # Email (for magic links)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Override with environment variables if they exist
if os.getenv("DATABASE_URL"):
    settings.DATABASE_URL = os.getenv("DATABASE_URL")
if os.getenv("REDIS_URL"):
    settings.REDIS_URL = os.getenv("REDIS_URL")
if os.getenv("OPENAI_API_KEY"):
    settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if os.getenv("PINECONE_API_KEY"):
    settings.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")