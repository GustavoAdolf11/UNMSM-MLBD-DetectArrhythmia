"""
DTO para señales ECG
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ECGSignalDTO:
    """DTO para representar una señal ECG."""
    id: str
    sampling_rate: int
    duration: float
    derivation: str
    sample_count: int
    created_at: datetime
    patient_id: Optional[str] = None
    is_valid_for_analysis: bool = True
