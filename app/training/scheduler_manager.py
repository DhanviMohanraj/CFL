"""DriftAdapt Scheduler Manager.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, Any

from app.training.trainer_exceptions import OptimizerConfigurationError


class SchedulerManager:
    """Manages initialization of learning rate schedulers."""
    
    def create_scheduler(self, optimizer: torch.optim.Optimizer, config: Dict[str, Any], total_steps: int) -> torch.optim.lr_scheduler.LRScheduler:
        """Creates the configured learning rate scheduler."""
        sched_name = config.get("scheduler", "cosine").lower()
        warmup_steps = config.get("warmup_steps", 100)
        
        if sched_name == "cosine":
            return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_steps)
        elif sched_name == "linear":
            return torch.optim.lr_scheduler.LinearLR(optimizer, total_iters=total_steps)
        elif sched_name == "constant":
            return torch.optim.lr_scheduler.ConstantLR(optimizer)
        else:
            raise OptimizerConfigurationError(f"Unsupported scheduler: {sched_name}")
