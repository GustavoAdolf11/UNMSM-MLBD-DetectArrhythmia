"""
Signal Processor Service
Maneja el preprocesamiento de señales ECG: filtrado, detección de picos, extracción de ventanas.
"""
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from typing import List, Tuple
from dataclasses import dataclass

from src.domain.entities import ECGSignal
from src.domain.value_objects import SignalWindow, RRInterval


@dataclass
class ProcessedSignalData:
    """Datos procesados de una señal ECG."""
    windows: List[SignalWindow]
    rr_intervals: List[RRInterval]
    r_peaks: np.ndarray


class SignalProcessor:
    """
    Servicio de infraestructura para procesamiento de señales ECG.
    """
    
    def __init__(self, sampling_rate: int = 360, window_size: int = 360):
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.half_window = window_size // 2
    
    def bandpass_filter(
        self,
        signal: np.ndarray,
        low: float = 0.5,
        high: float = 40.0,
        order: int = 4
    ) -> np.ndarray:
        """Aplica filtro pasa-banda a la señal."""
        nyquist = 0.5 * self.sampling_rate
        low_norm = low / nyquist
        high_norm = high / nyquist
        b, a = butter(order, [low_norm, high_norm], btype='band')
        return filtfilt(b, a, signal, method="gust")
    
    def detect_r_peaks(self, signal: np.ndarray) -> np.ndarray:
        """
        Detecta picos R en la señal ECG.
        Usa scipy.signal.find_peaks con parámetros ajustados para ECG.
        """
        # Parámetros para detección de picos R
        # distance: mínimo 200ms entre picos (360*0.2 = 72 muestras)
        # prominence: altura relativa del pico
        peaks, properties = find_peaks(
            signal,
            distance=int(0.2 * self.sampling_rate),  # 200ms
            prominence=0.3 * np.std(signal),
            height=np.mean(signal)
        )
        return peaks
    
    def extract_windows_and_rr(
        self,
        signal: np.ndarray,
        r_peaks: np.ndarray
    ) -> Tuple[List[SignalWindow], List[RRInterval]]:
        """
        Extrae ventanas centradas en picos R y calcula intervalos RR.
        """
        windows = []
        rr_intervals = []
        
        # Calcular intervalos RR en segundos
        rr_samples = np.diff(r_peaks)
        rr_seconds = rr_samples / self.sampling_rate
        
        for i, peak in enumerate(r_peaks):
            # Verificar que la ventana cabe en la señal
            start = peak - self.half_window
            end = peak + self.half_window
            
            if start < 0 or end > len(signal):
                continue
            
            # Extraer ventana
            window_data = signal[start:end]
            
            # Crear SignalWindow normalizado
            window = SignalWindow.create_normalized(
                data=window_data,
                center_sample=peak,
                sampling_rate=self.sampling_rate
            )
            windows.append(window)
            
            # Calcular RR intervals
            rr_prev = rr_seconds[i-1] if i > 0 else rr_seconds[0] if len(rr_seconds) > 0 else 0.8
            rr_next = rr_seconds[i] if i < len(rr_seconds) else rr_seconds[-1] if len(rr_seconds) > 0 else 0.8
            
            rr_interval = RRInterval(previous=rr_prev, next=rr_next)
            rr_intervals.append(rr_interval)
        
        return windows, rr_intervals
    
    async def process_signal(self, ecg_signal: ECGSignal) -> ProcessedSignalData:
        """
        Procesa una señal ECG completa: filtrado, detección de picos, extracción de ventanas.
        
        Args:
            ecg_signal: Entidad de señal ECG del dominio
            
        Returns:
            Datos procesados listos para predicción
        """
        # 1. Aplicar filtro pasa-banda
        filtered_signal = self.bandpass_filter(ecg_signal.signal_data)
        
        # 2. Detectar picos R
        r_peaks = self.detect_r_peaks(filtered_signal)
        
        if len(r_peaks) < 2:
            # No hay suficientes latidos para analizar
            return ProcessedSignalData(windows=[], rr_intervals=[], r_peaks=r_peaks)
        
        # 3. Extraer ventanas y RR intervals
        windows, rr_intervals = self.extract_windows_and_rr(filtered_signal, r_peaks)
        
        return ProcessedSignalData(
            windows=windows,
            rr_intervals=rr_intervals,
            r_peaks=r_peaks
        )
    
    def estimate_qrs_width(self, window_data: np.ndarray) -> float:
        """
        Estima el ancho del complejo QRS en milisegundos.
        Aproximación basada en la envolvente de la derivada.
        """
        center = len(window_data) // 2
        
        # Calcular derivada y envolvente
        dv = np.abs(np.diff(window_data, prepend=window_data[0]))
        kernel = np.ones(5) / 5.0
        envelope = np.convolve(dv, kernel, mode='same')
        
        # Encontrar ancho usando umbral relativo
        peak_value = np.max(envelope[max(0, center-20):min(len(envelope), center+20)])
        threshold = 0.5 * peak_value
        
        # Buscar límites izquierdo y derecho
        left = center
        while left > 1 and envelope[left] > threshold:
            left -= 1
        
        right = center
        while right < len(envelope) - 2 and envelope[right] > threshold:
            right += 1
        
        width_samples = right - left
        width_ms = (width_samples / self.sampling_rate) * 1000.0
        
        return min(width_ms, 200.0)  # Cap at 200ms
