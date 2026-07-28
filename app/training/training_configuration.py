"""DriftAdapt Training Configuration.

Author: DriftAdapt Contributors
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.core.config.config_manager import ConfigManager


class TrainingConfiguration(BaseModel):
    """Pydantic model representing training configuration values."""
    experiment_name: str = "driftadapt_main"
    total_months: int = 12
    communication_rounds: int = 12
    local_epochs: int = 3
    batch_size: int = 4
    participation_rate: float = 1.0
    evaluation_interval: int = 1
    checkpoint_interval: int = 1
    auto_resume: bool = True
    random_seed: int = 42
    max_parallel_clients: int = 4
    aggregation_after_each_round: bool = True
    
    @classmethod
    def load_from_manager(cls, configs_dir: Optional[str] = None) -> "TrainingConfiguration":
        """Loads configuration utilizing the central ConfigManager."""
        manager = ConfigManager(configs_dir)
        config_data = getattr(manager.get_config(), "training", None)
        
        if config_data is None:
            return cls()
            
        if isinstance(config_data, dict):
             return cls(**config_data)
        return cls(**config_data.model_dump())
