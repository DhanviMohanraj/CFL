"""Tests for Metrics Validator.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.metrics_exceptions import MetricValidationFailed
from app.adapters.metrics_validator import MetricsValidator


def test_validate_numeric():
    validator = MetricsValidator()
    
    # Should pass
    validator.validate_numeric(10.0, "test")
    validator.validate_numeric(0.0, "test")
    validator.validate_numeric(-10.0, "test", allow_negative=True)
    
    with pytest.raises(MetricValidationFailed):
        validator.validate_numeric(-5.0, "test")


def test_validate_timestamp():
    validator = MetricsValidator()
    
    validator.validate_timestamp(1.0)
    
    with pytest.raises(MetricValidationFailed):
        validator.validate_timestamp(0.0)


def test_validate_unique():
    validator = MetricsValidator()
    
    ids = {"v1", "v2"}
    
    validator.validate_unique(ids, "v3")
    
    with pytest.raises(MetricValidationFailed):
        validator.validate_unique(ids, "v1")
