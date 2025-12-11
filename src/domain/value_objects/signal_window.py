"""
Value Object: Signal Window
Representa una ventana de señal ECG normalizada.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class SignalWindow:
    """
    Value Object inmutable que representa una ventana de señal ECG.
    """
    data: np.ndarray      # Datos de la ventana normalizada
    center_sample: int    # Muestra central (ubicación del pico R)
    sampling_rate: int    # Frecuencia de muestreo
    
    def __post_init__(self):
        """Validaciones al crear el value object."""
        if len(self.data) == 0:
            raise ValueError("Window data cannot be empty")
        
        if self.sampling_rate <= 0:
            raise ValueError("Sampling rate must be positive")
        
        if self.center_sample < 0:
            raise ValueError("Center sample must be non-negative")
    
    @property
    def window_size(self) -> int:
        """Retorna el tamaño de la ventana."""
        return len(self.data)
    
    @property
    def duration_seconds(self) -> float:
        """Retorna la duración de la ventana en segundos."""
        return self.window_size / self.sampling_rate
    
    def to_cnn_input(self) -> np.ndarray:
        """Prepara los datos para entrada CNN (añade dimensión de canal)."""
        return np.expand_dims(self.data, axis=-1).astype(np.float32)
    
    @classmethod
    def create_normalized(
        cls,
        data: np.ndarray,
        center_sample: int,
        sampling_rate: int
    ) -> "SignalWindow":
        """Factory method que crea una ventana con normalización z-score."""
        mean = np.mean(data)
        std = np.std(data)
        normalized = (data - mean) / (std + 1e-6)
        
        return cls(
            data=normalized.astype(np.float32),
            center_sample=center_sample,
            sampling_rate=sampling_rate
        )
