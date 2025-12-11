"""
Use Case: Analyze ECG Signal
Caso de uso para analizar y obtener información de una señal ECG sin predicción.
"""
import numpy as np
from src.domain.entities import ECGSignal
from src.application.dtos import ECGSignalDTO
from src.shared.exceptions import ValidationError


class AnalyzeECGSignalUseCase:
    """
    Use Case para analizar señales ECG y obtener información básica.
    """
    
    def __init__(self, signal_processor):
        self.signal_processor = signal_processor
    
    async def execute(self, signal_data: list, sampling_rate: int = 360) -> ECGSignalDTO:
        """
        Analiza una señal ECG y retorna información básica.
        
        Args:
            signal_data: Lista de valores de la señal
            sampling_rate: Frecuencia de muestreo en Hz
            
        Returns:
            DTO con información de la señal
        """
        try:
            # Crear entidad de dominio
            signal_array = np.array(signal_data, dtype=np.float32)
            ecg_signal = ECGSignal.create(
                signal_data=signal_array,
                sampling_rate=sampling_rate
            )
            
            # Validar
            ecg_signal.validate()
            
            # Crear DTO de respuesta
            return ECGSignalDTO(
                id=ecg_signal.id,
                sampling_rate=ecg_signal.sampling_rate,
                duration=ecg_signal.duration,
                derivation=ecg_signal.derivation,
                sample_count=ecg_signal.get_sample_count(),
                created_at=ecg_signal.created_at,
                patient_id=ecg_signal.patient_id,
                is_valid_for_analysis=ecg_signal.is_valid_for_analysis()
            )
            
        except Exception as e:
            raise ValidationError(f"Failed to analyze ECG signal: {str(e)}")
