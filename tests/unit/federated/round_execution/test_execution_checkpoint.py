"""Tests for Execution Checkpoint.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.execution_checkpoint import ExecutionCheckpoint
from app.federated.round_execution.execution_exceptions import RoundRecoveryError


def test_execution_checkpoint(tmp_path):
    ckpt = ExecutionCheckpoint(base_dir=str(tmp_path))
    
    path = ckpt.save_checkpoint("r1", "stage1", {})
    assert "r1_stage1.pt" in path
    
    with pytest.raises(RoundRecoveryError):
        ckpt.restore_checkpoint("r1", "stage1")
