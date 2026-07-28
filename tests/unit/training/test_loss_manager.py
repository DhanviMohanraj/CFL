"""Tests for Loss Manager.

Author: DriftAdapt Contributors
"""

import torch
from app.training.loss_manager import LossManager


def test_loss_manager():
    mgr = LossManager({})
    
    outputs = torch.randn(4, 10)
    targets = torch.randint(0, 10, (4,))
    
    loss1 = mgr.compute_loss(outputs, targets)
    loss2 = mgr.compute_loss(outputs, targets)
    
    avg_loss = mgr.get_epoch_train_loss()
    assert avg_loss > 0.0
    
    # Should be empty after fetching epoch loss
    assert mgr.get_epoch_train_loss() == 0.0
