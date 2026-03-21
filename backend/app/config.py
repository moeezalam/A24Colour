import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "A24 Style Transfer API"
    VERSION: str = "1.0.0"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # Processing Settings
    MAX_IMAGE_DIMENSION: int = 2048
    DEFAULT_JPEG_QUALITY: int = 95
    
    # Asset Paths
    ASSETS_PATH: str = os.path.join(os.path.dirname(__file__), "..", "assets")
    LUTS_PATH: str = os.path.join(ASSETS_PATH, "luts")
    GRAIN_TEXTURES_PATH: str = os.path.join(ASSETS_PATH, "grain_textures")
    MODELS_PATH: str = os.path.join(ASSETS_PATH, "models")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Redis Settings (for future use with Celery)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    class Config:
        case_sensitive = True

settings = Settings()