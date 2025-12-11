"""
Use Case: Predict Arrhythmia
Caso de uso principal para predecir arritmias en señales ECG.
"""
import time
import numpy as np
from typing import List, Optional
from datetime import datetime

from src.domain.entities import ECGSignal, ArrhythmiaPrediction
from src.domain.repositories import IPredictionRepository, IModelRepository
from src.application.dtos import PredictionRequestDTO, PredictionResponseDTO, BeatPredictionDTO
from src.shared.exceptions import ValidationError, PredictionError


class PredictArrhythmiaUseCase:
    """
    Use Case para predecir arritmias.
    Orquesta el flujo de negocio: preprocesamiento, predicción y persistencia.
    """
    
    def __init__(
        self,
        prediction_repository: IPredictionRepository,
        model_repository: IModelRepository,
        signal_processor,  # Inyectamos el procesador de señales
        predictor_service  # Inyectamos el servicio de predicción
    ):
        self.prediction_repository = prediction_repository
        self.model_repository = model_repository
        self.signal_processor = signal_processor
        self.predictor_service = predictor_service
    
    async def execute(self, request: PredictionRequestDTO) -> PredictionResponseDTO:
        """
        Ejecuta el caso de uso de predicción de arritmias.
        
        Args:
            request: DTO con los datos de la señal ECG
            
        Returns:
            DTO con los resultados de la predicción
            
        Raises:
            ValidationError: Si los datos de entrada son inválidos
            PredictionError: Si ocurre un error en la predicción
        """
        start_time = time.time()
        
        try:
            # 1. Crear entidad de dominio ECGSignal
            signal_array = np.array(request.signal_data, dtype=np.float32)
            ecg_signal = ECGSignal.create(
                signal_data=signal_array,
                sampling_rate=request.sampling_rate,
                derivation=request.derivation,
                patient_id=request.patient_id
            )
            
            # 2. Validar señal
            ecg_signal.validate()
            if not ecg_signal.is_valid_for_analysis(min_duration=5.0):
                raise ValidationError("ECG signal too short for reliable analysis")
            
            # 3. Procesar señal (filtrado, detección de picos R, extracción de ventanas)
            processed_data = await self.signal_processor.process_signal(ecg_signal)
            
            if len(processed_data.windows) == 0:
                raise PredictionError("No valid heartbeats detected in signal")
            
            # 4. Realizar predicción con el modelo
            predictions = await self.predictor_service.predict(
                processed_data,
                apply_ruleguard=request.apply_ruleguard
            )
            
            # 5. Crear entidad de predicción
            beat_predictions_dto = []
            normal_count = 0
            ventricular_count = 0
            
            for beat_pred in predictions.beat_predictions:
                if beat_pred['arrhythmia_type'] == 'N':
                    normal_count += 1
                else:
                    ventricular_count += 1
                
                beat_predictions_dto.append(BeatPredictionDTO(
                    beat_index=beat_pred['beat_index'],
                    position_sample=beat_pred['position_sample'],
                    arrhythmia_type=beat_pred['arrhythmia_type'],
                    confidence=beat_pred['confidence'],
                    rr_previous=beat_pred.get('rr_previous'),
                    rr_next=beat_pred.get('rr_next'),
                    qrs_width_ms=beat_pred.get('qrs_width_ms')
                ))
            
            # 6. Determinar clasificación general
            overall_type = 'V' if ventricular_count > 0 else 'N'
            overall_confidence = predictions.overall_confidence
            
            arrhythmia_prediction = ArrhythmiaPrediction.create(
                ecg_signal_id=ecg_signal.id,
                arrhythmia_type=overall_type,
                confidence=overall_confidence,
                threshold=predictions.threshold,
                beat_predictions=[bp.__dict__ for bp in beat_predictions_dto],
                metadata={
                    'total_beats': len(beat_predictions_dto),
                    'normal_beats': normal_count,
                    'ventricular_beats': ventricular_count,
                    'ruleguard_applied': request.apply_ruleguard
                }
            )
            
            # 7. Persistir predicción
            saved_prediction = await self.prediction_repository.save(arrhythmia_prediction)
            
            # 8. Calcular tiempo de procesamiento
            processing_time = (time.time() - start_time) * 1000  # ms
            
            # 9. Crear respuesta
            return PredictionResponseDTO(
                prediction_id=saved_prediction.id,
                ecg_signal_id=ecg_signal.id,
                overall_arrhythmia_type=overall_type,
                overall_confidence=overall_confidence,
                risk_level=saved_prediction.get_risk_level(),
                threshold_used=predictions.threshold,
                total_beats=len(beat_predictions_dto),
                normal_beats=normal_count,
                ventricular_beats=ventricular_count,
                beat_predictions=beat_predictions_dto,
                processing_time_ms=processing_time,
                created_at=saved_prediction.created_at,
                metadata=arrhythmia_prediction.metadata
            )
            
        except ValidationError:
            raise
        except Exception as e:
            raise PredictionError(f"Failed to predict arrhythmia: {str(e)}")
