"""
Repository Interface: Prediction Repository
Define el contrato para persistencia de predicciones.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import ArrhythmiaPrediction


class IPredictionRepository(ABC):
    """
    Interfaz del repositorio para predicciones de arritmias.
    Implementa el patrón Repository de DDD.
    """
    
    @abstractmethod
    async def save(self, prediction: ArrhythmiaPrediction) -> ArrhythmiaPrediction:
        """Guarda una predicción."""
        pass
    
    @abstractmethod
    async def find_by_id(self, prediction_id: str) -> Optional[ArrhythmiaPrediction]:
        """Busca una predicción por ID."""
        pass
    
    @abstractmethod
    async def find_by_ecg_signal_id(self, ecg_signal_id: str) -> List[ArrhythmiaPrediction]:
        """Busca todas las predicciones de una señal ECG."""
        pass
    
    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[ArrhythmiaPrediction]:
        """Lista todas las predicciones con paginación."""
        pass
    
    @abstractmethod
    async def delete(self, prediction_id: str) -> bool:
        """Elimina una predicción."""
        pass
