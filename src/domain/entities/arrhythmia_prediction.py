"""
Domain Entity: Arrhythmia Prediction
Representa una predicción de arritmia con su resultado y confianza.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List
from uuid import uuid4


@dataclass
class ArrhythmiaPrediction:
    """
    Entidad de dominio que representa una predicción de arritmia.
    """
    id: str
    ecg_signal_id: str
    arrhythmia_type: str      # 'N' (Normal) o 'V' (Ventricular)
    confidence: float         # Probabilidad [0, 1]
    threshold: float          # Umbral usado para clasificación
    created_at: datetime
    beat_predictions: Optional[List[Dict]] = None  # Predicciones por latido
    metadata: Optional[Dict] = None
    
    @classmethod
    def create(
        cls,
        ecg_signal_id: str,
        arrhythmia_type: str,
        confidence: float,
        threshold: float,
        beat_predictions: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> "ArrhythmiaPrediction":
        """Factory method para crear una predicción."""
        prediction = cls(
            id=str(uuid4()),
            ecg_signal_id=ecg_signal_id,
            arrhythmia_type=arrhythmia_type,
            confidence=confidence,
            threshold=threshold,
            created_at=datetime.utcnow(),
            beat_predictions=beat_predictions,
            metadata=metadata or {}
        )
        prediction.validate()
        return prediction
    
    def validate(self) -> bool:
        """Validaciones de dominio para la predicción."""
        if self.arrhythmia_type not in ['N', 'V']:
            raise ValueError("Arrhythmia type must be 'N' or 'V'")
        
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        
        if not 0 <= self.threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        return True
    
    def is_high_confidence(self, min_confidence: float = 0.80) -> bool:
        """Verifica si la predicción tiene alta confianza."""
        return self.confidence >= min_confidence
    
    def is_ventricular_arrhythmia(self) -> bool:
        """Verifica si es una arritmia ventricular."""
        return self.arrhythmia_type == 'V'
    
    def get_risk_level(self) -> str:
        """Retorna el nivel de riesgo basado en el tipo y confianza."""
        if self.arrhythmia_type == 'N':
            return "LOW"
        
        if self.confidence >= 0.85:
            return "HIGH"
        elif self.confidence >= 0.70:
            return "MEDIUM"
        else:
            return "LOW"
