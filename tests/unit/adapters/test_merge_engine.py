"""Tests for Adapter Merge Engine.

Author: DriftAdapt Contributors
"""

import pytest

try:
    import torch
except ImportError:
    pytest.skip("PyTorch is not available", allow_module_level=True)

from app.adapters.merge_engine import AdapterMergeEngine
from app.adapters.version_metadata import AdapterVersionMetadata
from app.adapters.merge_exceptions import DuplicateAdapterError


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test."""
    AdapterMergeEngine._instance = None
    yield


def create_mock_metadata(vid: str, cid: str) -> AdapterVersionMetadata:
    return AdapterVersionMetadata(
        version_id=vid,
        adapter_id="base",
        clinic_id=cid,
        communication_round=1,
        local_training_round=1,
        version_number=1,
        checksum="hash",
        parameter_count=100,
        adapter_size_bytes=100,
        serialization_format="torch"
    )


def test_merge_two_adapters():
    engine = AdapterMergeEngine()
    engine._strict_validation = False
    
    state1 = {"lora_A.weight": torch.ones(2, 2)}
    state2 = {"lora_A.weight": torch.ones(2, 2) * 3}
    
    m1 = create_mock_metadata("c1_round_1_v1", "c1")
    m2 = create_mock_metadata("c2_round_1_v1", "c2")
    
    merged_state, metadata = engine.merge_states([state1, state2], [m1, m2])
    
    # 1 + 3 / 2 = 2
    assert torch.all(merged_state["lora_A.weight"] == 2.0)
    assert metadata.participating_clinics == ["c1", "c2"] or metadata.participating_clinics == ["c2", "c1"]


def test_merge_five_adapters():
    engine = AdapterMergeEngine()
    engine._strict_validation = False
    
    states = [{"lora_A.weight": torch.ones(2, 2) * i} for i in range(5)]
    metadatas = [create_mock_metadata(f"c{i}_round_1_v1", f"c{i}") for i in range(5)]
    
    merged_state, metadata = engine.merge_states(states, metadatas)
    
    # 0 + 1 + 2 + 3 + 4 = 10 / 5 = 2
    assert torch.all(merged_state["lora_A.weight"] == 2.0)
    assert len(metadata.participating_clinics) == 5


def test_merge_identical_adapters():
    engine = AdapterMergeEngine()
    engine._strict_validation = False
    
    state1 = {"lora_A.weight": torch.ones(2, 2) * 2}
    state2 = {"lora_A.weight": torch.ones(2, 2) * 2}
    
    m1 = create_mock_metadata("c1_round_1_v1", "c1")
    m2 = create_mock_metadata("c2_round_1_v1", "c2")
    
    merged_state, metadata = engine.merge_states([state1, state2], [m1, m2])
    
    assert torch.all(merged_state["lora_A.weight"] == 2.0)


def test_duplicate_inputs():
    engine = AdapterMergeEngine()
    engine._allow_duplicate_inputs = False
    
    state1 = {"lora_A.weight": torch.ones(2, 2)}
    m1 = create_mock_metadata("c1_round_1_v1", "c1")
    
    with pytest.raises(DuplicateAdapterError):
        engine.merge_states([state1, state1], [m1, m1])
