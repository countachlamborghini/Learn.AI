"""Configuration settings for Global Brain application."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/globalbrain"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Pinecone
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west1-gcp-free"
    pinecone_index_name: str = "globalbrain-embeddings"
    
    # AWS S3
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-west-2"
    s3_bucket_name: str = "globalbrain-documents"
    
    # Stripe
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # Application
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf", ".docx", ".pptx", ".jpg", ".jpeg", ".png"]
    
    # LLM Settings
    default_model: str = "gpt-3.5-turbo"
    max_tokens_per_request: int = 2000
    temperature: float = 0.7
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"


settings = Settings()