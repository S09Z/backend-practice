from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict, Any

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
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_SSL: bool = False
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: str = "100/minute"
    
    # Rate limits by endpoint
    RATE_LIMITS: Dict[str, str] = {
        "default": "100/minute",
        "auth_login": "10/hour",
        "auth_register": "5/hour", 
        "api_read": "1000/hour",
        "api_write": "200/hour",
        "health": "1000/minute",  # High limit for health checks
    }
    
    # Rate limits by user type
    USER_TYPE_RATE_LIMITS: Dict[str, Dict[str, str]] = {
        "anonymous": {
            "default": "50/hour",
            "auth_login": "10/hour",
            "auth_register": "3/hour",
        },
        "authenticated": {
            "default": "1000/hour",
            "api_read": "5000/hour",
            "api_write": "1000/hour",
        },
        "premium": {
            "default": "10000/hour",
            "api_read": "50000/hour", 
            "api_write": "10000/hour",
        }
    }
    
    # IP Whitelist (no rate limiting)
    RATE_LIMIT_WHITELIST: List[str] = [
        "127.0.0.1",
        "::1",
        # Add your monitoring IPs here
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()