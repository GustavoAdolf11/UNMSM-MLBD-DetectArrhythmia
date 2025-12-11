"""
Pydantic schemas for prediction endpoints
"""
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    """Schema para solicitud de predicción."""
    signal_data: List[float] = Field(
        ...,
        description="ECG signal data points",
        min_length=360,
        examples=[[0.1, 0.2, 0.3]]
    )
    sampling_rate: int = Field(
        default=360,
        description="Sampling rate in Hz",
        ge=100,
        le=1000
    )
    derivation: str = Field(
        default="MLII",
        description="ECG derivation (MLII, V5, etc.)"
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Optional patient identifier"
    )
    apply_ruleguard: bool = Field(
        default=True,
        description="Apply RuleGuard to reduce false positives"
    )
    
    @field_validator('signal_data')
    @classmethod
    def validate_signal_data(cls, v):
        if len(v) < 360:
            raise ValueError('Signal must have at least 360 samples')
        return v


class BeatPredictionResponse(BaseModel):
    """Schema para predicción individual de un latido."""
    beat_index: int = Field(description="Beat index in the signal")
    position_sample: int = Field(description="Sample position of R peak")
    arrhythmia_type: str = Field(description="'N' for Normal, 'V' for Ventricular")
    confidence: float = Field(description="Prediction confidence [0-1]", ge=0, le=1)
    rr_previous: Optional[float] = Field(default=None, description="Previous RR interval (seconds)")
    rr_next: Optional[float] = Field(default=None, description="Next RR interval (seconds)")
    qrs_width_ms: Optional[float] = Field(default=None, description="QRS complex width in ms")


class PredictionResponse(BaseModel):
    """Schema para respuesta de predicción."""
    prediction_id: str = Field(description="Unique prediction identifier")
    ecg_signal_id: str = Field(description="ECG signal identifier")
    overall_arrhythmia_type: str = Field(description="Overall classification: 'N' or 'V'")
    overall_confidence: float = Field(description="Overall confidence score", ge=0, le=1)
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, HIGH")
    threshold_used: float = Field(description="Classification threshold used")
    total_beats: int = Field(description="Total number of heartbeats analyzed")
    normal_beats: int = Field(description="Number of normal beats")
    ventricular_beats: int = Field(description="Number of ventricular beats")
    beat_predictions: List[BeatPredictionResponse] = Field(description="Predictions for each beat")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    created_at: datetime = Field(description="Prediction timestamp")
    metadata: Optional[Dict] = Field(default=None, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
                "ecg_signal_id": "123e4567-e89b-12d3-a456-426614174001",
                "overall_arrhythmia_type": "N",
                "overall_confidence": 0.95,
                "risk_level": "LOW",
                "threshold_used": 0.5,
                "total_beats": 10,
                "normal_beats": 10,
                "ventricular_beats": 0,
                "beat_predictions": [],
                "processing_time_ms": 245.3,
                "created_at": "2025-12-10T12:00:00",
                "metadata": {}
            }
        }
    }


class HealthResponse(BaseModel):
    """Schema para health check."""
    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    model_loaded: bool = Field(description="Whether ML model is loaded")
    timestamp: datetime = Field(description="Current timestamp")
