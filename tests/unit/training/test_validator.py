"""Tests for Experiment Validator.

Author: DriftAdapt Contributors
"""

import pytest
from app.training.experiment_validator import ExperimentValidator
from app.training.training_configuration import TrainingConfiguration
from app.training.experiment_exceptions import ExperimentValidationError


def test_validator_configuration():
    validator = ExperimentValidator()
    
    # Valid config
    config = TrainingConfiguration()
    validator.validate_configuration(config)
    
    # Invalid configs
    with pytest.raises(ExperimentValidationError):
        invalid_config = TrainingConfiguration(total_months=0)
        validator.validate_configuration(invalid_config)
        
    with pytest.raises(ExperimentValidationError):
        invalid_config = TrainingConfiguration(participation_rate=1.5)
        validator.validate_configuration(invalid_config)

def test_validator_clinics():
    validator = ExperimentValidator()
    
    validator.validate_clinics(["clinic_01"])
    
    with pytest.raises(ExperimentValidationError):
        validator.validate_clinics([])
