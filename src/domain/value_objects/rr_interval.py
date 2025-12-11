"""
Value Object: RR Interval
Representa los intervalos RR entre latidos consecutivos.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RRInterval:
    """
    Value Object inmutable que representa intervalos RR.
    Los intervalos RR son importantes para detectar arritmias.
    """
    previous: float  # RR interval anterior (segundos)
    next: float      # RR interval siguiente (segundos)
    
    def __post_init__(self):
        """Validaciones al crear el value object."""
        if self.previous < 0 or self.next < 0:
            raise ValueError("RR intervals must be non-negative")
    
    @property
    def ratio(self) -> float:
        """Calcula el ratio entre el siguiente y el anterior."""
        if self.previous == 0:
            return float('inf')
        return self.next / self.previous
    
    @property
    def average(self) -> float:
        """Calcula el promedio de los intervalos."""
        return (self.previous + self.next) / 2.0
    
    def is_irregular(self, threshold: float = 0.20) -> bool:
        """
        Detecta si hay irregularidad significativa.
        threshold: diferencia relativa permitida
        """
        if self.previous == 0:
            return True
        diff_ratio = abs(self.next - self.previous) / self.previous
        return diff_ratio > threshold
    
    def to_features(self) -> list:
        """Convierte a lista de features para el modelo."""
        return [self.previous, self.next, self.ratio]
