"""DriftAdapt Dataset Dispatcher.

Author: DriftAdapt Contributors
"""

from typing import Dict, Optional
from app.training.experiment_exceptions import DatasetDispatchError


class DatasetDispatcher:
    """Dispatches dataset paths for specific clinic and month."""
    
    def __init__(self, base_dataset_path: str = "datasets") -> None:
        self.base_dataset_path = base_dataset_path
        
    def dispatch(self, clinic_id: str, month: int) -> str:
        """Constructs and returns the dataset path for the given clinic and month."""
        if not clinic_id:
            raise DatasetDispatchError("clinic_id is required.")
        if month <= 0:
            raise DatasetDispatchError("month must be greater than 0.")
            
        return f"{self.base_dataset_path}/{clinic_id}/month_{month:02d}.jsonl"
