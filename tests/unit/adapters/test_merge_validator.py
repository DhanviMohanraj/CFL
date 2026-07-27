"""Tests for Merge Validator.

Author: DriftAdapt Contributors
"""

import pytest

try:
    import torch
except ImportError:
    pytest.skip("PyTorch is not available", allow_module_level=True)

from app.adapters.merge_validator import MergeValidator
from app.adapters.merge_exceptions import (
    EmptyMergeInput,
    DuplicateAdapterError,
    TensorShapeMismatch,
    IncompatibleAdapters,
)


def test_empty_input():
    validator = MergeValidator()
    with pytest.raises(EmptyMergeInput):
        validator.validate_inputs([], [])
        
    with pytest.raises(EmptyMergeInput):
        validator.validate_inputs([{"a": 1}], ["v1"])


def test_duplicate_adapters():
    validator = MergeValidator()
    with pytest.raises(DuplicateAdapterError):
        validator.validate_inputs([{"a": 1}, {"a": 1}], ["v1", "v1"])


def test_shape_mismatch():
    validator = MergeValidator()
    
    state1 = {"lora_A": torch.ones(2, 2)}
    state2 = {"lora_A": torch.ones(3, 3)}
    
    with pytest.raises(TensorShapeMismatch):
        validator.validate_inputs([state1, state2], ["v1", "v2"])


def test_parameter_name_mismatch():
    validator = MergeValidator()
    
    state1 = {"lora_A": torch.ones(2, 2)}
    state2 = {"lora_B": torch.ones(2, 2)}
    
    with pytest.raises(IncompatibleAdapters, match="Parameter names mismatch"):
        validator.validate_inputs([state1, state2], ["v1", "v2"])


def test_dtype_mismatch():
    validator = MergeValidator()
    
    state1 = {"lora_A": torch.ones(2, 2, dtype=torch.float32)}
    state2 = {"lora_A": torch.ones(2, 2, dtype=torch.float16)}
    
    with pytest.raises(IncompatibleAdapters, match="Dtype mismatch"):
        validator.validate_inputs([state1, state2], ["v1", "v2"])
