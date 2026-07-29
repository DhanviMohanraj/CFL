"""DriftAdapt Dataset Loader.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional
from datasets import load_dataset, Dataset
import os

class DatasetLoader:
    """Loads healthcare datasets."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def load(self, clinic_id: str, month: int) -> Optional[Dataset]:
        """Loads dataset for the given clinic and month."""
        dataset_dir = self.config.get("dataset_dir", "datasets")
        
        file_path = os.path.join(dataset_dir, clinic_id, f"month_{month:02d}.jsonl")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset not found at {file_path}")
            
        dataset = load_dataset("json", data_files=file_path, split="train")
        return dataset
