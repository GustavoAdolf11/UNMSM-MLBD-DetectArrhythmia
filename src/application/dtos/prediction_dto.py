"""
DTOs relacionados con predicciones de arritmias
"""
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class PredictionRequestDTO:
    """DTO para solicitud de predicción."""
    signal_data: List[float]
    sampling_rate: int = 360
    derivation: str = "MLII"
    patient_id: Optional[str] = None
    apply_ruleguard: bool = True


@dataclass
class BeatPredictionDTO:
    """DTO para predicción individual de un latido."""
    beat_index: int
    position_sample: int
    arrhythmia_type: str  # 'N' o 'V'
    confidence: float
    rr_previous: Optional[float] = None
    rr_next: Optional[float] = None
    qrs_width_ms: Optional[float] = None


@dataclass
class PredictionResponseDTO:
    """DTO para respuesta de predicción."""
    prediction_id: str
    ecg_signal_id: str
    overall_arrhythmia_type: str
    overall_confidence: float
    risk_level: str
    threshold_used: float
    total_beats: int
    normal_beats: int
    ventricular_beats: int
    beat_predictions: List[BeatPredictionDTO]
    processing_time_ms: float
    created_at: datetime
    metadata: Optional[Dict] = None
