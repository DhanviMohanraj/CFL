"""Tests for Version History Manager.

Author: DriftAdapt Contributors
"""

import time

from app.adapters.version_history import VersionHistoryManager
from app.adapters.version_metadata import AdapterVersionMetadata


def create_mock_version(vid: str, cid: str, parent: str = None, t_offset: int = 0) -> AdapterVersionMetadata:
    return AdapterVersionMetadata(
        version_id=vid,
        adapter_id="base",
        clinic_id=cid,
        communication_round=1,
        local_training_round=1,
        version_number=1,
        parent_version=parent,
        created_at=time.time() + t_offset,
        checksum="hash",
        parameter_count=100,
        adapter_size_bytes=100
    )


def test_lineage_and_history():
    """Test history sorting, parent lookups, and lineage traversal."""
    v1 = create_mock_version("clinic1_round_1_v1", "clinic1", t_offset=1)
    v2 = create_mock_version("clinic1_round_2_v2", "clinic1", parent="clinic1_round_1_v1", t_offset=2)
    v3 = create_mock_version("clinic1_round_3_v3", "clinic1", parent="clinic1_round_2_v2", t_offset=3)
    
    versions = {v1.version_id: v1, v2.version_id: v2, v3.version_id: v3}
    manager = VersionHistoryManager()
    
    # Test history sorting
    history = manager.get_history(versions, "clinic1")
    assert [v.version_id for v in history] == ["clinic1_round_1_v1", "clinic1_round_2_v2", "clinic1_round_3_v3"]
    
    # Test latest
    assert manager.get_latest(versions, "clinic1").version_id == "clinic1_round_3_v3"
    
    # Test lineage (backward tracing)
    lineage = manager.get_lineage(versions, "clinic1_round_3_v3")
    assert [v.version_id for v in lineage] == ["clinic1_round_3_v3", "clinic1_round_2_v2", "clinic1_round_1_v1"]
    
    # Test find children
    children = manager.find_children(versions, "clinic1_round_1_v1")
    assert len(children) == 1
    assert children[0].version_id == "clinic1_round_2_v2"
