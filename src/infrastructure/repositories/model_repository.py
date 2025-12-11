"""
Model Repository Implementation
Implementa la carga y gestión de modelos ML.
"""
import os
import json
from pathlib import Path
from typing import Any, Optional, Dict
import tensorflow as tf

from src.domain.repositories import IModelRepository
from src.shared.exceptions import ModelNotFoundError


class ModelRepository(IModelRepository):
    """
    Implementación del repositorio de modelos ML.
    Carga y cachea modelos TensorFlow/Keras.
    """
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self._model_cache: Dict[str, Any] = {}
        self._metadata_cache: Dict[str, dict] = {}
    
    async def load_model(self, model_name: str) -> Any:
        """
        Carga un modelo ML desde disco (con cache).
        
        Args:
            model_name: Nombre del modelo (ej: 'model_v7')
            
        Returns:
            Modelo de TensorFlow/Keras cargado
        """
        # Revisar cache
        if model_name in self._model_cache:
            return self._model_cache[model_name]
        
        # Buscar archivo .keras
        model_path = self.model_dir / f"{model_name}.keras"
        
        if not model_path.exists():
            raise ModelNotFoundError(f"Model not found: {model_path}")
        
        # Cargar modelo
        try:
            model = tf.keras.models.load_model(model_path, compile=False)
            self._model_cache[model_name] = model
            return model
        except Exception as e:
            raise ModelNotFoundError(f"Failed to load model {model_name}: {str(e)}")
    
    async def get_model_metadata(self, model_name: str) -> Optional[dict]:
        """
        Obtiene metadatos del modelo desde archivo JSON.
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            Diccionario con metadatos o None
        """
        # Revisar cache
        if model_name in self._metadata_cache:
            return self._metadata_cache[model_name]
        
        # Buscar archivo de metadatos
        meta_path = self.model_dir / f"meta_{model_name.replace('model_', '')}.json"
        
        if not meta_path.exists():
            return None
        
        try:
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            self._metadata_cache[model_name] = metadata
            return metadata
        except Exception:
            return None
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Verifica si el modelo está cargado en memoria."""
        return model_name in self._model_cache
