"""Tests for Aggregation Validator.

Author: DriftAdapt Contributors
"""

import torch
import pytest
from app.aggregation.aggregation_validator import AggregationValidator
from app.aggregation.aggregation_exceptions import ValidationFailure


def test_aggregation_validator():
    validator = AggregationValidator({})
    
    sd1 = {"A": torch.randn(10)}
    sd2 = {"A": torch.randn(10)}
    sd3 = {"A": torch.randn(5)}
    
    assert validator.validate_before_merge([sd1, sd2]) is True
    
    with pytest.raises(ValidationFailure):
        validator.validate_before_merge([sd1, sd3])
        
    assert validator.validate_after_merge(sd1) is True
    
    with pytest.raises(ValidationFailure):
        validator.validate_after_merge({"A": torch.tensor([float("nan")])})
