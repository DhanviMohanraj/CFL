"""DriftAdapt Training Services Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies the integrity of isolated training services (optimizers, early stopping, etc).
"""

import pytest
import torch
from torch.nn import Linear, Parameter

from app.schemas.training_config import TrainingConfiguration
from app.services.training.optimizer_service import OptimizerService
from app.services.training.scheduler_service import SchedulerService
from app.services.training.early_stopping import EarlyStoppingService
from app.services.training.gradient_manager import GradientManager


def test_optimizer_service_adamw():
    service = OptimizerService()
    config = TrainingConfiguration(optimizer="adamw", learning_rate=1e-3, weight_decay=0.01)
    
    # Dummy parameter
    param = Parameter(torch.randn(10, 10))
    opt = service.create_optimizer([param], config)
    
    assert type(opt).__name__ == "AdamW"
    assert opt.param_groups[0]["lr"] == 1e-3
    assert opt.param_groups[0]["weight_decay"] == 0.01





def test_scheduler_service_linear():
    opt_service = OptimizerService()
    sched_service = SchedulerService()
    
    config = TrainingConfiguration(optimizer="adamw", scheduler="linear", warmup_steps=10)
    param = Parameter(torch.randn(10, 10))
    opt = opt_service.create_optimizer([param], config)
    
    scheduler = sched_service.create_scheduler(opt, config, num_training_steps=100)
    assert scheduler is not None


def test_early_stopping_improvement():
    early_stopping = EarlyStoppingService(patience=2, min_delta=0.01)
    
    is_best, stop = early_stopping.step(1.0)
    assert is_best is True
    assert stop is False
    
    is_best, stop = early_stopping.step(0.98) # Improvement > 0.01
    assert is_best is True
    assert stop is False


def test_early_stopping_trigger():
    early_stopping = EarlyStoppingService(patience=2, min_delta=0.01)
    
    early_stopping.step(1.0)
    
    # No improvement
    is_best, stop = early_stopping.step(0.995) 
    assert is_best is False
    assert stop is False
    
    # No improvement again -> Trigger
    is_best, stop = early_stopping.step(0.999)
    assert is_best is False
    assert stop is True


def test_gradient_manager_clipping():
    manager = GradientManager()
    config = TrainingConfiguration(max_grad_norm=1.0)
    
    layer = Linear(10, 10)
    # Fake large gradients
    for p in layer.parameters():
        p.grad = torch.ones_like(p) * 10.0
        
    opt = torch.optim.SGD(layer.parameters(), lr=0.1)
    
    stats = manager.step(layer, opt, config)
    assert stats["step_skipped"] is False
    assert stats["grad_norm"] > 1.0  # The original norm was large
    
    # We don't check p.grad here because zero_grad() was called, setting gradients to 0 or None.
