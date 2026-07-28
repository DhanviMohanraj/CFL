"""Tests for Checkpoint Manager.

Author: DriftAdapt Contributors
"""

import os
import pytest
from app.training.checkpoint_manager import CheckpointManager
from app.training.trainer_exceptions import CheckpointError


def test_checkpoint_manager(tmp_path):
    mgr = CheckpointManager(base_dir=str(tmp_path))
    
    path = mgr.save("trainer_1", 1, {}, is_best=True)
    assert path.endswith("trainer_1_epoch_1.pt")
    
    with pytest.raises(CheckpointError):
        mgr.load("trainer_1")
