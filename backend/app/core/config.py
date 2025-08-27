from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App
    app_name: str = "Global Brain Student Edition"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/globalbrain"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Vector DB
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    
    # S3/MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "globalbrain-docs"
    s3_region: str = "us-east-1"
    
    # AI/LLM
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # File upload
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf", ".docx", ".pptx", ".txt", ".png", ".jpg", ".jpeg"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()