"""
Arrhythmia Predictor Service
Servicio que realiza predicciones de arritmias usando el modelo ML.
"""
import numpy as np
from typing import List, Dict
from dataclasses import dataclass

from src.infrastructure.ml.signal_processor import ProcessedSignalData
from src.infrastructure.repositories.model_repository import ModelRepository
from src.shared.exceptions import PredictionError


@dataclass
class PredictionResult:
    """Resultado de predicción."""
    beat_predictions: List[Dict]
    overall_confidence: float
    threshold: float


class ArrhythmiaPredictor:
    """
    Servicio de predicción de arritmias.
    """
    
    def __init__(
        self,
        model_repository: ModelRepository,
        threshold: float = 0.5,
        ruleguard_config: dict = None
    ):
        self.model_repository = model_repository
        self.threshold = threshold
        self.ruleguard_config = ruleguard_config or {
            'rr_low': 0.90,
            'rr_high': 1.10,
            'qrs_threshold': 110.0
        }
    
    async def predict(
        self,
        processed_data: ProcessedSignalData,
        apply_ruleguard: bool = True
    ) -> PredictionResult:
        """
        Realiza predicciones de arritmias en los latidos detectados.
        
        Args:
            processed_data: Datos de señal procesados
            apply_ruleguard: Si se aplica RuleGuard para reducir falsos positivos
            
        Returns:
            Resultado con predicciones por latido
        """
        if len(processed_data.windows) == 0:
            raise PredictionError("No windows to predict")
        
        # Cargar modelo
        model = await self.model_repository.load_model("model_v7")
        
        # Preparar inputs para el modelo
        # Input 1: Señales (batch, 360, 1)
        signal_inputs = np.stack([w.to_cnn_input() for w in processed_data.windows])
        
        # Input 2: RR intervals (batch, 3)
        rr_inputs = np.stack([rr.to_features() for rr in processed_data.rr_intervals]).astype(np.float32)
        
        # Predicción
        probabilities = model.predict(
            {'sig': signal_inputs, 'rr': rr_inputs},
            batch_size=256,
            verbose=0
        ).ravel()
        
        # Clasificación binaria
        predictions = (probabilities >= self.threshold).astype(np.int32)
        
        # Aplicar RuleGuard si está habilitado
        if apply_ruleguard:
            predictions = self._apply_ruleguard(
                predictions,
                processed_data,
                probabilities
            )
        
        # Construir resultados por latido
        beat_predictions = []
        for i, (window, rr, prob, pred) in enumerate(zip(
            processed_data.windows,
            processed_data.rr_intervals,
            probabilities,
            predictions
        )):
            arrhythmia_type = 'V' if pred == 1 else 'N'
            
            beat_predictions.append({
                'beat_index': i,
                'position_sample': int(window.center_sample),
                'arrhythmia_type': arrhythmia_type,
                'confidence': float(prob),
                'rr_previous': float(rr.previous),
                'rr_next': float(rr.next),
                'qrs_width_ms': None  # Se puede calcular si es necesario
            })
        
        # Confianza general (promedio de las predicciones V o confianza max)
        v_probs = probabilities[predictions == 1]
        overall_confidence = float(np.max(v_probs)) if len(v_probs) > 0 else float(1 - np.max(probabilities))
        
        return PredictionResult(
            beat_predictions=beat_predictions,
            overall_confidence=overall_confidence,
            threshold=self.threshold
        )
    
    def _apply_ruleguard(
        self,
        predictions: np.ndarray,
        processed_data: ProcessedSignalData,
        probabilities: np.ndarray
    ) -> np.ndarray:
        """
        Aplica reglas heurísticas para reducir falsos positivos de arritmias ventriculares.
        """
        filtered_predictions = predictions.copy()
        
        rr_low = self.ruleguard_config['rr_low']
        rr_high = self.ruleguard_config['rr_high']
        qrs_thr = self.ruleguard_config['qrs_threshold']
        
        for i, (window, rr, pred) in enumerate(zip(
            processed_data.windows,
            processed_data.rr_intervals,
            predictions
        )):
            if pred == 1:  # Solo para predicciones de V
                # Calcular ratio RR
                rr_ratio = rr.ratio
                
                # Si RR ratio está en rango "normal" y QRS no es ancho, posible FP
                if rr_low < rr_ratio < rr_high:
                    # Calcular ancho QRS aproximado
                    from src.infrastructure.ml.signal_processor import SignalProcessor
                    processor = SignalProcessor()
                    qrs_width = processor.estimate_qrs_width(window.data)
                    
                    if qrs_width < qrs_thr:
                        # Probablemente es un falso positivo
                        filtered_predictions[i] = 0
        
        return filtered_predictions
