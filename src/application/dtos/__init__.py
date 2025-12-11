"""
DTOs (Data Transfer Objects) para la capa de aplicación
"""
from .prediction_dto import PredictionRequestDTO, PredictionResponseDTO, BeatPredictionDTO
from .ecg_signal_dto import ECGSignalDTO

__all__ = [
    'PredictionRequestDTO',
    'PredictionResponseDTO',
    'BeatPredictionDTO',
    'ECGSignalDTO'
]
