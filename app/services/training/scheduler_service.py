"""DriftAdapt Scheduler Service.

Author: DriftAdapt Contributors
Purpose: Configures learning rate schedulers for the training loop.
"""

from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler
from transformers import get_scheduler

from app.schemas.training_config import TrainingConfiguration
from app.core.logging import LoggerFactory


class SchedulerService:
    """Service for configuring learning rate schedules."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("SchedulerService")

    def create_scheduler(self, optimizer: Optimizer, config: TrainingConfiguration,
                         num_training_steps: int) -> LRScheduler:
        """Creates a learning rate scheduler based on training configuration.

        Args:
            optimizer: The configured PyTorch optimizer.
            config: Training hyperparameters.
            num_training_steps: Total number of optimization steps.

        Returns:
            Configured PyTorch LRScheduler.
        """
        self._logger.info(
            f"Initializing {config.scheduler} scheduler with {config.warmup_steps} warmup steps "
            f"over {num_training_steps} total steps."
        )

        from torch.optim.lr_scheduler import LRScheduler
        import typing
        scheduler = get_scheduler(
            name=config.scheduler,
            optimizer=optimizer,
            num_warmup_steps=config.warmup_steps,
            num_training_steps=num_training_steps
        )
        return typing.cast(LRScheduler, scheduler)
