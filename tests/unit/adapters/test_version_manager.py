"""Tests for Adapter Version Manager.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.exceptions import VersionAlreadyExists, VersionNotFound
from app.adapters.lifecycle import VersionState
from app.adapters.version_manager import AdapterVersionManager
from app.adapters.version_metadata import AdapterVersionMetadata


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test."""
    AdapterVersionManager._instance = None
    yield


def create_mock_version(vid: str, cid: str) -> AdapterVersionMetadata:
    return AdapterVersionMetadata(
        version_id=vid,
        adapter_id="base",
        clinic_id=cid,
        communication_round=1,
        local_training_round=1,
        version_number=1,
        checksum="hash",
        parameter_count=100,
        adapter_size_bytes=100
    )


def test_create_and_get_version():
    """Test singleton lifecycle for version creation and retrieval."""
    manager = AdapterVersionManager()
    
    # Disable auto-save for testing isolated logic
    manager._policy.auto_save = False
    manager._policy.auto_backup = False
    
    v = create_mock_version("clinic1_round_1_v1", "clinic1")
    manager.create_version(v)
    
    # Verify retrieval
    retrieved = manager.get_version("clinic1_round_1_v1")
    assert retrieved.version_id == "clinic1_round_1_v1"
    
    # Status should have automatically transitioned from CREATED to ACTIVE
    assert retrieved.status == VersionState.ACTIVE.value
    
    # Verify duplicate prevention
    with pytest.raises(VersionAlreadyExists):
        manager.create_version(v)


def test_delete_version():
    """Test soft deletion transitions version to DELETED."""
    manager = AdapterVersionManager()
    manager._policy.auto_save = False
    manager._policy.auto_backup = False
    
    v = create_mock_version("clinic1_round_1_v1", "clinic1")
    manager.create_version(v)
    
    manager.delete_version("clinic1_round_1_v1")
    deleted = manager.get_version("clinic1_round_1_v1")
    
    assert deleted.status == VersionState.DELETED.value


def test_search_versions():
    """Test filtering mechanism over version registries."""
    manager = AdapterVersionManager()
    manager._policy.auto_save = False
    manager._policy.auto_backup = False
    
    v1 = create_mock_version("clinic1_round_1_v1", "clinic1")
    v2 = create_mock_version("clinic2_round_1_v1", "clinic2")
    
    manager.create_version(v1)
    manager.create_version(v2)
    
    results = manager.search_versions(clinic_id="clinic1")
    assert len(results) == 1
    assert results[0].version_id == "clinic1_round_1_v1"
