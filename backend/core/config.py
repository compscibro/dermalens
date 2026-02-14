"""
Core configuration settings for DermaLens
Uses pydantic-settings for environment variable management
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Project info
    PROJECT_NAME: str = "DermaLens"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/dermalens"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "dermalens-images"
    S3_PRESIGNED_URL_EXPIRATION: int = 3600  # 1 hour
    
    # NanoBanana AI
    NANOBANANA_API_KEY: Optional[str] = None
    NANOBANANA_BASE_URL: str = "https://api.nanobanana.ai/v1"
    
    # Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    
    # Treatment Plan Settings
    MIN_TREATMENT_DAYS: int = 14  # 2 weeks minimum
    MAX_TREATMENT_DAYS: int = 28  # 4 weeks maximum
    SCORE_DECLINE_THRESHOLD: float = 10.0  # % decline to trigger adjustment
    SEVERE_IRRITATION_THRESHOLD: float = 20.0  # % for immediate adjustment
    
    # Scan Settings
    MIN_SCAN_INTERVAL_DAYS: int = 7  # Weekly scans
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/jpg", "image/png"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
