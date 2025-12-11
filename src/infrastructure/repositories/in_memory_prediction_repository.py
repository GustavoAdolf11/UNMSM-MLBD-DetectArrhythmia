"""
In-Memory Prediction Repository Implementation
Implementa persistencia en memoria (para desarrollo/testing).
Para producción, usar DB real (PostgreSQL, MongoDB, etc).
"""
from typing import List, Optional, Dict
from datetime import datetime

from src.domain.entities import ArrhythmiaPrediction
from src.domain.repositories import IPredictionRepository
from src.shared.exceptions import RepositoryError


class InMemoryPredictionRepository(IPredictionRepository):
    """
    Repositorio en memoria para predicciones.
    Solo para desarrollo. En producción usar DB real.
    """
    
    def __init__(self):
        self._storage: Dict[str, ArrhythmiaPrediction] = {}
    
    async def save(self, prediction: ArrhythmiaPrediction) -> ArrhythmiaPrediction:
        """Guarda una predicción en memoria."""
        try:
            self._storage[prediction.id] = prediction
            return prediction
        except Exception as e:
            raise RepositoryError(f"Failed to save prediction: {str(e)}")
    
    async def find_by_id(self, prediction_id: str) -> Optional[ArrhythmiaPrediction]:
        """Busca una predicción por ID."""
        return self._storage.get(prediction_id)
    
    async def find_by_ecg_signal_id(self, ecg_signal_id: str) -> List[ArrhythmiaPrediction]:
        """Busca todas las predicciones de una señal ECG."""
        return [
            pred for pred in self._storage.values()
            if pred.ecg_signal_id == ecg_signal_id
        ]
    
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[ArrhythmiaPrediction]:
        """Lista todas las predicciones con paginación."""
        all_predictions = list(self._storage.values())
        # Ordenar por fecha de creación (más reciente primero)
        all_predictions.sort(key=lambda x: x.created_at, reverse=True)
        return all_predictions[offset:offset + limit]
    
    async def delete(self, prediction_id: str) -> bool:
        """Elimina una predicción."""
        if prediction_id in self._storage:
            del self._storage[prediction_id]
            return True
        return False
    
    def clear(self):
        """Limpia todo el storage (útil para testing)."""
        self._storage.clear()
