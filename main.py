"""
Main entry point for the FastAPI application
"""
import uvicorn
from src.presentation.app import app
from src.infrastructure.config.settings import settings


if __name__ == "__main__":
    uvicorn.run(
        "src.presentation.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
