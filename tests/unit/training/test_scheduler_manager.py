"""Tests for Scheduler Manager.

Author: DriftAdapt Contributors
"""

import torch
import torch.nn as nn
import pytest

from app.training.scheduler_manager import SchedulerManager
from app.training.trainer_exceptions import OptimizerConfigurationError


def test_scheduler_manager():
    mgr = SchedulerManager()
    
    # Mock optimizer
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = nn.Linear(10, 10)
    model = DummyModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    
    cosine = mgr.create_scheduler(optimizer, {"scheduler": "cosine"}, 100)
    assert isinstance(cosine, torch.optim.lr_scheduler.CosineAnnealingLR)
    
    linear = mgr.create_scheduler(optimizer, {"scheduler": "linear"}, 100)
    assert isinstance(linear, torch.optim.lr_scheduler.LinearLR)
    
    constant = mgr.create_scheduler(optimizer, {"scheduler": "constant"}, 100)
    assert isinstance(constant, torch.optim.lr_scheduler.ConstantLR)
    
    with pytest.raises(OptimizerConfigurationError):
        mgr.create_scheduler(optimizer, {"scheduler": "invalid_scheduler"}, 100)
