# Core module - Configuration and utilities

import os
from functools import lru_cache
from typing import Optional

class Settings:
    """Application settings from environment variables"""
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/petqr")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 168  # 7 days
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PetQR"
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
