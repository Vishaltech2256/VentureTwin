from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

from typing import Optional

class Settings(BaseSettings):
    # Database configurations
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432

    # Security configurations
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg2://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
