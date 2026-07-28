"""Tests for Optimizer Manager.

Author: DriftAdapt Contributors
"""

import torch
import torch.nn as nn
import pytest

from app.training.optimizer_manager import OptimizerManager
from app.training.trainer_exceptions import OptimizerConfigurationError


def test_optimizer_manager():
    mgr = OptimizerManager()
    
    # Mock model
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = nn.Linear(10, 10)
            
    model = DummyModel()
    
    adamw = mgr.create_optimizer(model.parameters(), {"optimizer": "adamw", "learning_rate": 1e-4})
    assert isinstance(adamw, torch.optim.AdamW)
    assert adamw.param_groups[0]["lr"] == 1e-4
    
    sgd = mgr.create_optimizer(model.parameters(), {"optimizer": "sgd", "learning_rate": 1e-3})
    assert isinstance(sgd, torch.optim.SGD)
    assert sgd.param_groups[0]["lr"] == 1e-3
    
    with pytest.raises(OptimizerConfigurationError):
        mgr.create_optimizer(model.parameters(), {"optimizer": "invalid_optimizer"})
