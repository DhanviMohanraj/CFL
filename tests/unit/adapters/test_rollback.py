"""Tests for Rollback Engine.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.exceptions import RollbackFailed, VersionNotFound
from app.adapters.lifecycle import VersionState
from app.adapters.rollback import RollbackEngine
from app.adapters.version_metadata import AdapterVersionMetadata


def create_mock_version(vid: str, cid: str, status: VersionState = VersionState.ACTIVE) -> AdapterVersionMetadata:
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
        status=status.value
    )


def test_successful_rollback():
    """Test rolling back to a valid active version."""
    v1 = create_mock_version("clinic1_round_1_v1", "clinic1")
    versions = {v1.version_id: v1}
    engine = RollbackEngine()
    
    result = engine.execute_rollback(versions, "clinic1", "clinic1_round_1_v1")
    assert result.status == VersionState.ROLLED_BACK.value


def test_rollback_wrong_clinic():
    """Test rollback fails when targeting another clinic's version."""
    v1 = create_mock_version("clinic1_round_1_v1", "clinic1")
    versions = {v1.version_id: v1}
    engine = RollbackEngine()
    
    with pytest.raises(RollbackFailed, match="belong to clinic wrong_clinic"):
        engine.execute_rollback(versions, "wrong_clinic", "clinic1_round_1_v1")


def test_rollback_deleted():
    """Test rollback fails when targeting a deleted version."""
    v1 = create_mock_version("clinic1_round_1_v1", "clinic1", status=VersionState.DELETED)
    versions = {v1.version_id: v1}
    engine = RollbackEngine()
    
    with pytest.raises(RollbackFailed, match="deleted"):
        engine.execute_rollback(versions, "clinic1", "clinic1_round_1_v1")


def test_rollback_checksum_failure():
    """Test rollback fails when physical checksum injection fails."""
    v1 = create_mock_version("clinic1_round_1_v1", "clinic1")
    versions = {v1.version_id: v1}
    engine = RollbackEngine()
    
    # Inject a failing checksum validator
    def bad_checksum(v: AdapterVersionMetadata) -> bool:
        return False
        
    with pytest.raises(RollbackFailed, match="Checksum verification failed"):
        engine.execute_rollback(versions, "clinic1", "clinic1_round_1_v1", verify_checksum_fn=bad_checksum)
