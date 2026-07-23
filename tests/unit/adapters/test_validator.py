"""Tests for Adapter State Validator.

Author: DriftAdapt Contributors
"""

import pytest

try:
    import torch
except ImportError:
    pytest.skip("PyTorch is not available", allow_module_level=True)

from app.adapters.exceptions import ValidationFailed
from app.adapters.validator import AdapterStateValidator


def test_successful_validation():
    """Test validation passes on valid state dict."""
    state = {"lora_A.weight": torch.randn(2, 10)}
    validator = AdapterStateValidator(strict=True)
    report = validator.validate(state)
    assert report.success is True
    assert report.parameter_count == 1
    assert not report.errors


def test_empty_state():
    """Test validation fails on empty state dict."""
    validator = AdapterStateValidator(strict=True)
    with pytest.raises(ValidationFailed, match="empty"):
        validator.validate({})


def test_invalid_dtype():
    """Test validation catches non-tensor values."""
    state = {"lora_A.weight": "not a tensor"}
    validator = AdapterStateValidator(strict=True)
    with pytest.raises(ValidationFailed, match="torch.Tensor"):
        validator.validate(state)


def test_shape_mismatch():
    """Test cross-validation catches shape mismatches."""
    state = {"lora_A.weight": torch.randn(2, 10)}
    ref_state = {"lora_A.weight": torch.randn(3, 10)}  # mismatch
    
    validator = AdapterStateValidator(strict=True)
    with pytest.raises(ValidationFailed, match="Shape mismatch"):
        validator.validate(state, reference_state=ref_state)


def test_unexpected_parameters():
    """Test cross-validation catches extra/unexpected parameters."""
    state = {
        "lora_A.weight": torch.randn(2, 10),
        "lora_B.weight": torch.randn(10, 2)
    }
    ref_state = {"lora_A.weight": torch.randn(2, 10)}
    
    validator = AdapterStateValidator(strict=True)
    with pytest.raises(ValidationFailed, match="unexpected"):
        validator.validate(state, reference_state=ref_state)


def test_missing_parameters():
    """Test cross-validation catches missing parameters."""
    state = {"lora_A.weight": torch.randn(2, 10)}
    ref_state = {
        "lora_A.weight": torch.randn(2, 10),
        "lora_B.weight": torch.randn(10, 2)
    }
    
    validator = AdapterStateValidator(strict=True)
    with pytest.raises(ValidationFailed, match="Missing"):
        validator.validate(state, reference_state=ref_state)
