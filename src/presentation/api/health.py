"""
Health check and status endpoints
"""
from fastapi import APIRouter, Depends
from datetime import datetime

from src.presentation.schemas import HealthResponse
from src.infrastructure.repositories import ModelRepository
from src.infrastructure.config.dependencies import get_model_repository
from src.infrastructure.config.settings import settings

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API health and model status"
)
async def health_check(
    model_repo: ModelRepository = Depends(get_model_repository)
) -> HealthResponse:
    """
    Endpoint de health check.
    Verifica que la API está funcionando y que el modelo está cargado.
    """
    model_loaded = model_repo.is_model_loaded("model_v7")
    
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        version=settings.APP_VERSION,
        model_loaded=model_loaded,
        timestamp=datetime.utcnow()
    )


@router.get(
    "/",
    summary="Root endpoint",
    description="API information"
)
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
