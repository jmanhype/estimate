"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Uses Pydantic Settings for validation and type safety.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "staging", "production", "test"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql://estimate:estimate@localhost:5432/estimate_dev"  # type: ignore[assignment]
    )
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=20, ge=0, le=100)
    db_pool_timeout: int = Field(default=30, ge=1, le=300)
    db_echo: bool = False

    # Redis Cache
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")  # type: ignore[assignment]
    redis_max_connections: int = Field(default=10, ge=1, le=100)

    # API Settings
    api_title: str = "EstiMate API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])
    cors_allow_credentials: bool = True

    # Security / Supabase Authentication
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = Field(default=60, ge=5, le=43200)

    # Supabase settings (for JWT validation)
    supabase_url: str = Field(default="")
    supabase_anon_key: str = Field(default="")
    supabase_jwt_secret: str = Field(default="")  # JWT secret from Supabase project settings

    # AWS S3 Storage
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    aws_region: str = Field(default="us-east-1")
    s3_bucket_name: str = Field(default="estimate-uploads")
    s3_presigned_url_expiration: int = Field(default=3600, ge=60, le=86400)  # 1 hour default, max 24 hours


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application configuration
    """
    return Settings()


# Global settings instance
settings = get_settings()
