"""Tests for Validation Manager.

Author: DriftAdapt Contributors
"""

import torch
from app.training.validation_manager import ValidationManager


def test_validation_manager():
    mgr = ValidationManager({"early_stopping": True, "patience": 2})
    
    predictions = torch.tensor([1, 0, 1, 1])
    targets = torch.tensor([1, 0, 1, 0])
    
    metrics = mgr.evaluate(predictions, targets)
    assert metrics["accuracy"] == 0.75
    
    stop, is_best = mgr.check_early_stopping(0.5)
    assert is_best is True
    assert stop is False
    
    stop, is_best = mgr.check_early_stopping(0.6)
    assert is_best is False
    assert stop is False
    
    stop, is_best = mgr.check_early_stopping(0.7)
    assert is_best is False
    assert stop is True
