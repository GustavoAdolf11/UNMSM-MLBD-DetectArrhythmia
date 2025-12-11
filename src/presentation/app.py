"""
FastAPI Application Factory
Crea y configura la aplicación FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.infrastructure.config.settings import settings
from src.presentation.api import predictions_router, health_router
from src.shared.exceptions import DomainException


def create_app() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API REST para detección de arritmias en señales ECG usando Deep Learning",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Registrar routers
    app.include_router(health_router)
    app.include_router(predictions_router, prefix=settings.API_V1_PREFIX)
    
    # Exception handlers
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request, exc):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "type": exc.__class__.__name__}
        )
    
    # Startup event: precargar modelo
    @app.on_event("startup")
    async def startup_event():
        """Precarga el modelo ML al iniciar la aplicación."""
        from src.infrastructure.config.dependencies import get_container
        container = get_container()
        try:
            await container.model_repository.load_model("model_v7")
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not preload model: {e}")
    
    return app


# Instancia de la aplicación
app = create_app()
