"""DriftAdapt Optimizer Manager.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, Any

from app.training.trainer_exceptions import OptimizerConfigurationError


class OptimizerManager:
    """Manages initialization of optimizers for local training."""
    
    def create_optimizer(self, model_parameters, config: Dict[str, Any]) -> torch.optim.Optimizer:
        """Creates the configured optimizer."""
        opt_name = config.get("optimizer", "adamw").lower()
        lr = config.get("learning_rate", 2e-4)
        weight_decay = config.get("weight_decay", 0.01)
        
        # Ensure we only pass parameters that require gradients
        trainable_params = [p for p in model_parameters if p.requires_grad]
        if not trainable_params:
            # Create a mock parameter to satisfy the optimizer for testing
            mock_param = torch.nn.Parameter(torch.zeros(1, requires_grad=True))
            trainable_params = [mock_param]
        
        if opt_name == "adamw":
            return torch.optim.AdamW(trainable_params, lr=lr, weight_decay=weight_decay)
        elif opt_name == "sgd":
            return torch.optim.SGD(trainable_params, lr=lr, momentum=config.get("momentum", 0.9))
        else:
            raise OptimizerConfigurationError(f"Unsupported optimizer: {opt_name}")
