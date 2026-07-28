"""Tests for Checkpoint Scheduler.

Author: DriftAdapt Contributors
"""

import os
import pytest

from app.federated.client.checkpoint_scheduler import CheckpointScheduler


def test_checkpoint_rotation(tmp_path):
    scheduler = CheckpointScheduler(str(tmp_path), max_checkpoints=2)
    
    # Save 3 checkpoints
    scheduler.save_checkpoint(1, 0.5, b"weights_1")
    scheduler.save_checkpoint(2, 0.4, b"weights_2")
    scheduler.save_checkpoint(3, 0.3, b"weights_3")
    
    latest = scheduler.get_latest()
    assert latest is not None
    assert latest.epoch == 3
    
    # Assert that only 2 checkpoints remain
    assert len(scheduler._checkpoints) == 2
    assert scheduler._checkpoints[0].epoch == 2
    assert scheduler._checkpoints[1].epoch == 3
    
    scheduler.clean_all()
    assert len(scheduler._checkpoints) == 0
