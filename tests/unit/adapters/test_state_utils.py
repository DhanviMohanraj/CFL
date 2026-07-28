"""Tests for Adapter State Utilities.

Author: DriftAdapt Contributors
"""

import pytest

try:
    import torch
    import torch.nn as nn
except ImportError:
    pytest.skip("PyTorch is not available", allow_module_level=True)

from app.adapters.state_utils import AdapterStateManager, calculate_size


class DummyModel(nn.Module):
    """A dummy PEFT-like model for testing extraction."""
    def __init__(self):
        super().__init__()
        self.base_layer = nn.Linear(10, 10)
        self.lora_A = nn.Linear(10, 2)
        self.lora_B = nn.Linear(2, 10)


def test_extract_state():
    """Test extraction of only LoRA parameters."""
    model = DummyModel()
    manager = AdapterStateManager()
    
    extracted = manager.extract_state(model)
    
    assert len(extracted) == 4  # weight and bias for lora_A and lora_B
    assert all("lora_" in k for k in extracted.keys())
    assert "base_layer.weight" not in extracted


def test_clone_state():
    """Test deep cloning of state tensors."""
    model = DummyModel()
    manager = AdapterStateManager()
    extracted = manager.extract_state(model)
    
    cloned = manager.clone_state(extracted)
    assert manager.compare_states(extracted, cloned)
    
    # Modifying the clone should not modify the original extracted state
    cloned["lora_A.weight"][0, 0] = 999.0
    assert not manager.compare_states(extracted, cloned)


def test_count_parameters():
    """Test parameter count calculation."""
    model = DummyModel()
    manager = AdapterStateManager()
    extracted = manager.extract_state(model)
    
    # lora_A: 10*2 + 2 = 22
    # lora_B: 2*10 + 10 = 30
    # Total = 52
    assert manager.count_parameters(extracted) == 52


def test_calculate_size():
    """Test byte size calculation for a state dictionary."""
    model = DummyModel()
    manager = AdapterStateManager()
    extracted = manager.extract_state(model)
    
    sizes = calculate_size(extracted)
    assert "bytes" in sizes
    assert "kb" in sizes
    assert "mb" in sizes
    assert "communication_cost" in sizes
    assert sizes["bytes"] > 0
