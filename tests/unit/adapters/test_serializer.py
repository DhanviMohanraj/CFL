"""Tests for Adapter Serializer.

Author: DriftAdapt Contributors
"""

import pytest

try:
    import torch
except ImportError:
    pytest.skip("PyTorch is not available", allow_module_level=True)

from app.adapters.serializer import AdapterSerializer


def test_serialize_deserialize():
    """Test byte serialization and deserialization of torch tensors."""
    state = {
        "lora_A.weight": torch.randn(2, 10),
        "lora_B.weight": torch.randn(10, 2)
    }
    serializer = AdapterSerializer()
    
    data = serializer.serialize(state)
    assert isinstance(data, bytes)
    assert len(data) > 0
    
    loaded = serializer.deserialize(data)
    assert len(loaded) == 2
    assert torch.equal(state["lora_A.weight"], loaded["lora_A.weight"])


def test_save_load(tmp_path):
    """Test disk IO operations for adapter states."""
    state = {"lora_A.weight": torch.randn(2, 10)}
    serializer = AdapterSerializer()
    
    file_path = tmp_path / "test_adapter.bin"
    serializer.save(state, file_path)
    assert file_path.exists()
    
    loaded = serializer.load(file_path)
    assert torch.equal(state["lora_A.weight"], loaded["lora_A.weight"])
    
def test_estimate_size():
    """Test fast size estimation."""
    state = {"lora_A.weight": torch.randn(200, 1000)}
    serializer = AdapterSerializer()
    
    size_bytes = serializer.estimate_size(state)
    assert size_bytes > 0
    assert size_bytes == len(serializer.serialize(state))
