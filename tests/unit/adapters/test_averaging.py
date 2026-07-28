"""Tests for Averaging Merge Strategy.

Author: DriftAdapt Contributors
"""

import pytest

try:
    import torch
except ImportError:
    pytest.skip("PyTorch is not available", allow_module_level=True)

from app.adapters.averaging import NaiveAverageMerge


def test_arithmetic_averaging():
    """Test mathematically accurate arithmetic mean."""
    strategy = NaiveAverageMerge()
    
    state1 = {
        "lora_A.weight": torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
        "lora_B.weight": torch.tensor([10.0, 20.0])
    }
    state2 = {
        "lora_A.weight": torch.tensor([[3.0, 4.0], [5.0, 6.0]]),
        "lora_B.weight": torch.tensor([30.0, 40.0])
    }
    
    merged = strategy.merge([state1, state2])
    
    # lora_A mean
    assert torch.equal(merged["lora_A.weight"], torch.tensor([[2.0, 3.0], [4.0, 5.0]]))
    
    # lora_B mean
    assert torch.equal(merged["lora_B.weight"], torch.tensor([20.0, 30.0]))


def test_strategy_metadata():
    """Test strategy metadata responses."""
    strategy = NaiveAverageMerge()
    assert strategy.strategy_name() == "naive_average"
    assert strategy.supports_weighting() is False
