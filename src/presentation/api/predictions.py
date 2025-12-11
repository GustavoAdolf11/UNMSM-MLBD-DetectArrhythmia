"""
Prediction API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.presentation.schemas import PredictionRequest, PredictionResponse
from src.application.use_cases import PredictArrhythmiaUseCase
from src.application.dtos import PredictionRequestDTO, BeatPredictionDTO
from src.infrastructure.config.dependencies import get_predict_use_case
from src.shared.exceptions import ValidationError, PredictionError

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post(
    "/",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Predict arrhythmia in ECG signal",
    description="Analyzes an ECG signal and predicts whether it contains normal (N) or ventricular (V) arrhythmias"
)
async def predict_arrhythmia(
    request: PredictionRequest,
    use_case: PredictArrhythmiaUseCase = Depends(get_predict_use_case)
) -> PredictionResponse:
    """
    Endpoint para predecir arritmias en una señal ECG.
    
    - **signal_data**: Lista de valores de la señal ECG
    - **sampling_rate**: Frecuencia de muestreo en Hz (default: 360)
    - **derivation**: Derivación ECG (default: MLII)
    - **patient_id**: ID opcional del paciente
    - **apply_ruleguard**: Aplicar filtro de falsos positivos (default: true)
    """
    try:
        # Convertir request a DTO
        request_dto = PredictionRequestDTO(
            signal_data=request.signal_data,
            sampling_rate=request.sampling_rate,
            derivation=request.derivation,
            patient_id=request.patient_id,
            apply_ruleguard=request.apply_ruleguard
        )
        
        # Ejecutar use case
        result = await use_case.execute(request_dto)
        
        # Convertir DTO a schema de respuesta
        return PredictionResponse(
            prediction_id=result.prediction_id,
            ecg_signal_id=result.ecg_signal_id,
            overall_arrhythmia_type=result.overall_arrhythmia_type,
            overall_confidence=result.overall_confidence,
            risk_level=result.risk_level,
            threshold_used=result.threshold_used,
            total_beats=result.total_beats,
            normal_beats=result.normal_beats,
            ventricular_beats=result.ventricular_beats,
            beat_predictions=[
                {
                    "beat_index": bp.beat_index,
                    "position_sample": bp.position_sample,
                    "arrhythmia_type": bp.arrhythmia_type,
                    "confidence": bp.confidence,
                    "rr_previous": bp.rr_previous,
                    "rr_next": bp.rr_next,
                    "qrs_width_ms": bp.qrs_width_ms
                }
                for bp in result.beat_predictions
            ],
            processing_time_ms=result.processing_time_ms,
            created_at=result.created_at,
            metadata=result.metadata
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PredictionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
