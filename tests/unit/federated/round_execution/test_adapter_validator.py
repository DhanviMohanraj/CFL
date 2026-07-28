"""Tests for Adapter Validator.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.adapter_validator import AdapterValidator
from app.federated.round_execution.execution_exceptions import AdapterValidationError


def test_adapter_validator():
    validator = AdapterValidator()
    
    assert validator.validate("path/to/adapter.pt", {"checksum": "123"}) is True
    
    with pytest.raises(AdapterValidationError):
        validator.validate("", {"checksum": "123"})
        
    with pytest.raises(AdapterValidationError):
        validator.validate("path", {})
