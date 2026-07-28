"""Tests for Redistribution Manager.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.redistribution_manager import RedistributionManager
from app.federated.round_execution.execution_exceptions import RedistributionError


def test_redistribution_manager():
    manager = RedistributionManager()
    
    res = manager.redistribute("path", ["c1", "c2"])
    assert res["c1"] == "success"
    
    with pytest.raises(RedistributionError):
        manager.redistribute("", ["c1"])
