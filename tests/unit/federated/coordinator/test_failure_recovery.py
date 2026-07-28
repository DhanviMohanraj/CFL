"""Tests for Failure Recovery.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.coordinator.failure_recovery import FailureRecovery
from app.federated.coordinator.coordinator_schema import FederatedRoundMetadata
from app.federated.coordinator.coordinator_exceptions import RoundRecoveryError


def test_failure_recovery_proceed():
    recovery = FailureRecovery(allow_partial=True)
    
    meta = FederatedRoundMetadata(
        round_id="r1",
        global_round=1,
        selected_clients=["c1", "c2", "c3"],
        completed_clients=["c1", "c2"],
        failed_clients=["c3"]
    )
    
    # Min clients is 2, 2 completed, partial allowed
    assert recovery.can_proceed(meta, min_clients=2) is True
    
    # Min clients is 3, 2 completed -> fails
    assert recovery.can_proceed(meta, min_clients=3) is False
    
    recovery_no_partial = FailureRecovery(allow_partial=False)
    # Failures exist, partial not allowed
    assert recovery_no_partial.can_proceed(meta, min_clients=2) is False

def test_failure_recovery_attempt():
    recovery = FailureRecovery()
    meta = FederatedRoundMetadata(
        round_id="r1",
        global_round=1
    )
    
    with pytest.raises(RoundRecoveryError):
        recovery.recover_round(meta)
