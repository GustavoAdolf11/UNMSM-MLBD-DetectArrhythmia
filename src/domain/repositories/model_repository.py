"""
Repository Interface: Model Repository
Define el contrato para carga y gestión de modelos ML.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class IModelRepository(ABC):
    """
    Interfaz del repositorio para modelos de Machine Learning.
    """
    
    @abstractmethod
    async def load_model(self, model_name: str) -> Any:
        """Carga un modelo ML desde disco."""
        pass
    
    @abstractmethod
    async def get_model_metadata(self, model_name: str) -> Optional[dict]:
        """Obtiene metadatos del modelo."""
        pass
    
    @abstractmethod
    def is_model_loaded(self, model_name: str) -> bool:
        """Verifica si el modelo está cargado en memoria."""
        pass
