"""
Configuration settings for the application
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "ECG Arrhythmia Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # ML Model settings
    MODEL_NAME: str = "model_v7"
    MODEL_DIR: Path = Path(__file__).parent.parent.parent.parent / "models" / "ecg_nv_cnn"
    MODEL_THRESHOLD: float = 0.5
    
    # Signal processing settings
    SAMPLING_RATE: int = 360
    WINDOW_SIZE: int = 360
    DERIVATION_INDEX: int = 0
    
    # RuleGuard settings
    USE_RULEGUARD: bool = True
    RULEGUARD_RR_LOW: float = 0.90
    RULEGUARD_RR_HIGH: float = 1.10
    RULEGUARD_QRS_THRESHOLD: float = 110.0
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
