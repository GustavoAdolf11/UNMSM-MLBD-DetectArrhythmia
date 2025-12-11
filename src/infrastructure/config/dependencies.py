"""
Dependency Injection Container
Configura e inyecta dependencias.
"""
from functools import lru_cache
from pathlib import Path

from src.infrastructure.config.settings import settings
from src.infrastructure.repositories import ModelRepository, InMemoryPredictionRepository
from src.infrastructure.ml import SignalProcessor, ArrhythmiaPredictor
from src.application.use_cases import PredictArrhythmiaUseCase, AnalyzeECGSignalUseCase


class DependencyContainer:
    """Contenedor de dependencias (Singleton)."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Repositories
        self.model_repository = ModelRepository(model_dir=settings.MODEL_DIR)
        self.prediction_repository = InMemoryPredictionRepository()
        
        # Services
        self.signal_processor = SignalProcessor(
            sampling_rate=settings.SAMPLING_RATE,
            window_size=settings.WINDOW_SIZE
        )
        
        ruleguard_config = {
            'rr_low': settings.RULEGUARD_RR_LOW,
            'rr_high': settings.RULEGUARD_RR_HIGH,
            'qrs_threshold': settings.RULEGUARD_QRS_THRESHOLD
        }
        
        self.predictor_service = ArrhythmiaPredictor(
            model_repository=self.model_repository,
            threshold=settings.MODEL_THRESHOLD,
            ruleguard_config=ruleguard_config
        )
        
        # Use Cases
        self.predict_arrhythmia_use_case = PredictArrhythmiaUseCase(
            prediction_repository=self.prediction_repository,
            model_repository=self.model_repository,
            signal_processor=self.signal_processor,
            predictor_service=self.predictor_service
        )
        
        self.analyze_ecg_signal_use_case = AnalyzeECGSignalUseCase(
            signal_processor=self.signal_processor
        )
        
        self._initialized = True


@lru_cache()
def get_container() -> DependencyContainer:
    """Obtiene el contenedor de dependencias (singleton)."""
    return DependencyContainer()


# Funciones de inyección de dependencias para FastAPI
def get_predict_use_case() -> PredictArrhythmiaUseCase:
    """Inyecta el use case de predicción."""
    return get_container().predict_arrhythmia_use_case


def get_analyze_use_case() -> AnalyzeECGSignalUseCase:
    """Inyecta el use case de análisis."""
    return get_container().analyze_ecg_signal_use_case


def get_model_repository() -> ModelRepository:
    """Inyecta el repositorio de modelos."""
    return get_container().model_repository
