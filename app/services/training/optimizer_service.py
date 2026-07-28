"""DriftAdapt Optimizer Service.

Author: DriftAdapt Contributors
Purpose: Configures PyTorch optimizers based on training configurations.
"""

from typing import Iterable, Any
from torch.optim import Optimizer, AdamW, SGD
from app.schemas.training_config import TrainingConfiguration
from app.core.logging import LoggerFactory

try:
    from transformers import Adafactor
except ImportError:
    Adafactor = None  # type: ignore


class OptimizerService:
    """Service for selecting and configuring PyTorch optimizers."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("OptimizerService")

    def create_optimizer(self, parameters: Iterable[Any], config: TrainingConfiguration) -> Optimizer:
        """Creates the appropriate optimizer for the given trainable parameters.

        Args:
            parameters: Iterable of PyTorch parameters requiring gradients.
            config: The training configuration object.

        Returns:
            Configured PyTorch Optimizer.

        Raises:
            ValueError: If the requested optimizer is not supported.
        """
        opt_type = config.optimizer.lower()
        self._logger.info(f"Initializing {opt_type} optimizer with lr={config.learning_rate}, wd={config.weight_decay}")

        if opt_type == "adamw":
            return AdamW(
                parameters,
                lr=config.learning_rate,
                weight_decay=config.weight_decay
            )
        elif opt_type == "sgd":
            return SGD(
                parameters,
                lr=config.learning_rate,
                weight_decay=config.weight_decay,
                momentum=0.9
            )
        elif opt_type == "adafactor":
            if Adafactor is None:
                raise ImportError("transformers is not installed, cannot use Adafactor.")
            return Adafactor(
                parameters,
                lr=config.learning_rate,
                weight_decay=config.weight_decay,
                scale_parameter=False,
                relative_step=False
            )
        else:
            raise ValueError(f"Unsupported optimizer type: {opt_type}")
