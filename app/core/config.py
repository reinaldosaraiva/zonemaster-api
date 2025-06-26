import secrets
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "zonemaster-api"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    DATABASE_URL_SYNC: str = "sqlite:///./app.db"
    
    # Zonemaster API
    ZONEMASTER_API_URL: str = "http://localhost:8080/RPC2"
    ZONEMASTER_API_TIMEOUT: int = 300  # 5 minutes
    
    # Environment
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # First superuser
    FIRST_SUPERUSER_EMAIL: str = "admin@zonemaster-api.com"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
