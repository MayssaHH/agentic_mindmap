from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Agentic Mindmap API"
    API_VERSION: str = "1.0.0"
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    # PDF Processing Settings
    PDF_DPI: int = 300
    PDF_MAX_PAGES: Optional[int] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
