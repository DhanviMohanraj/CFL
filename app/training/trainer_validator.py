"""DriftAdapt Trainer Validator.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.training.trainer_exceptions import ValidationError, OptimizerConfigurationError


class TrainerValidator:
    """Validates configuration for local training."""
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validates training configuration parameters."""
        if config.get("local_epochs", 0) <= 0:
            raise ValidationError("local_epochs must be > 0")
        if config.get("batch_size", 0) <= 0:
            raise ValidationError("batch_size must be > 0")
        if config.get("learning_rate", 0.0) <= 0.0:
            raise OptimizerConfigurationError("learning_rate must be > 0")
