from functools import lru_cache
from typing import List

from pydantic import BaseSettings, AnyUrl, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Global Brain API"
    VERSION: str = "0.1.0"

    BACKEND_CORS_ORIGINS: List[AnyUrl | str] = ["*"]

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "db"
    POSTGRES_DB: str = "global_brain"

    REDIS_URL: str = "redis://redis:6379/0"

    S3_ENDPOINT_URL: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    class Config:
        case_sensitive = True
        env_file = ".env"

    @property
    def database_uri(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> Settings:  # pragma: no cover
    return Settings()