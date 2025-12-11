"""
Domain Entity: ECG Signal
Representa una señal ECG con sus propiedades y comportamientos del dominio.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import numpy as np
from uuid import uuid4


@dataclass
class ECGSignal:
    """
    Entidad de dominio que representa una señal ECG.
    """
    id: str
    signal_data: np.ndarray  # Datos crudos de la señal
    sampling_rate: int       # Frecuencia de muestreo (Hz)
    duration: float          # Duración en segundos
    derivation: str          # Derivación (MLII, V5, etc.)
    created_at: datetime
    patient_id: Optional[str] = None
    metadata: Optional[dict] = None
    
    @classmethod
    def create(
        cls,
        signal_data: np.ndarray,
        sampling_rate: int,
        derivation: str = "MLII",
        patient_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> "ECGSignal":
        """Factory method para crear una nueva señal ECG."""
        duration = len(signal_data) / sampling_rate
        
        return cls(
            id=str(uuid4()),
            signal_data=signal_data,
            sampling_rate=sampling_rate,
            duration=duration,
            derivation=derivation,
            created_at=datetime.utcnow(),
            patient_id=patient_id,
            metadata=metadata or {}
        )
    
    def validate(self) -> bool:
        """Validaciones de dominio para la señal ECG."""
        if self.signal_data is None or len(self.signal_data) == 0:
            raise ValueError("Signal data cannot be empty")
        
        if self.sampling_rate <= 0:
            raise ValueError("Sampling rate must be positive")
        
        if self.duration <= 0:
            raise ValueError("Duration must be positive")
        
        return True
    
    def get_sample_count(self) -> int:
        """Retorna el número de muestras en la señal."""
        return len(self.signal_data)
    
    def is_valid_for_analysis(self, min_duration: float = 10.0) -> bool:
        """Verifica si la señal es válida para análisis (duración mínima)."""
        return self.duration >= min_duration
