from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    PROJECT_NAME: str = "FastAPI Application"
    PROJECT_DESCRIPTION: str = "A FastAPI application with Prisma ORM"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database (Prisma uses DATABASE_URL)
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/mydb"
    # For SQLite: "file:./dev.db"
    # For MySQL: "mysql://user:password@localhost:3306/mydb"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

settings = Settings()