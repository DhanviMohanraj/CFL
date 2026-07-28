"""Tests for Execution Validator.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.execution_validator import ExecutionValidator
from app.federated.round_execution.execution_exceptions import RoundInitializationError


def test_execution_validator():
    validator = ExecutionValidator()
    
    validator.validate_round_config({"max_parallel_clients": 4, "client_timeout": 60})
    
    with pytest.raises(RoundInitializationError):
        validator.validate_round_config({"max_parallel_clients": 0, "client_timeout": 60})
        
    validator.validate_clients(["c1"])
    
    with pytest.raises(RoundInitializationError):
        validator.validate_clients([])
