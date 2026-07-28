"""Tests for Merge Compatibility Checker.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.compatibility import CompatibilityChecker
from app.adapters.version_metadata import AdapterVersionMetadata
from app.adapters.merge_exceptions import IncompatibleAdapters


def create_mock_metadata(vid: str, cid: str, params: int = 100, format: str = "torch") -> AdapterVersionMetadata:
    return AdapterVersionMetadata(
        version_id=vid,
        adapter_id="base",
        clinic_id=cid,
        communication_round=1,
        local_training_round=1,
        version_number=1,
        checksum="hash",
        parameter_count=params,
        adapter_size_bytes=100,
        serialization_format=format
    )


def test_valid_compatibility():
    checker = CompatibilityChecker()
    m1 = create_mock_metadata("c1_round_1_v1", "c1")
    m2 = create_mock_metadata("c2_round_1_v1", "c2")
    
    # Should pass without exception
    checker.verify_compatibility([m1, m2])


def test_different_parameter_count():
    checker = CompatibilityChecker()
    m1 = create_mock_metadata("c1_round_1_v1", "c1", params=100)
    m2 = create_mock_metadata("c2_round_1_v1", "c2", params=200)
    
    with pytest.raises(IncompatibleAdapters, match="Parameter count mismatch"):
        checker.verify_compatibility([m1, m2])


def test_different_serialization():
    checker = CompatibilityChecker()
    m1 = create_mock_metadata("c1_round_1_v1", "c1", format="torch")
    m2 = create_mock_metadata("c2_round_1_v1", "c2", format="safetensors")
    
    with pytest.raises(IncompatibleAdapters, match="Serialization format mismatch"):
        checker.verify_compatibility([m1, m2])
