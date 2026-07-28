"""DriftAdapt Experiment Validator.

Author: DriftAdapt Contributors
"""

from typing import List
from app.training.training_configuration import TrainingConfiguration
from app.training.experiment_exceptions import ExperimentValidationError


class ExperimentValidator:
    """Validates the state and configuration before starting an experiment."""
    
    def validate_configuration(self, config: TrainingConfiguration) -> None:
        """Validates training configuration parameters."""
        if config.total_months <= 0:
            raise ExperimentValidationError("total_months must be > 0")
        if config.communication_rounds <= 0:
            raise ExperimentValidationError("communication_rounds must be > 0")
        if config.local_epochs <= 0:
            raise ExperimentValidationError("local_epochs must be > 0")
        if config.batch_size <= 0:
            raise ExperimentValidationError("batch_size must be > 0")
        if not (0.0 < config.participation_rate <= 1.0):
            raise ExperimentValidationError("participation_rate must be between 0.0 and 1.0")
            
    def validate_clinics(self, selected_clinics: List[str]) -> None:
        """Validates that at least one clinic is available."""
        if not selected_clinics:
            raise ExperimentValidationError("At least one clinic must be available to start the experiment.")
