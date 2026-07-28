"""DriftAdapt Gradient Manager.

Author: DriftAdapt Contributors
"""

import torch
import torch.nn as nn
from typing import Dict, Any


class GradientManager:
    """Handles gradient clipping and mixed precision scaling."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.gradient_clipping = config.get("gradient_clipping", 1.0)
        self.mixed_precision = config.get("mixed_precision", True)
        self.gradient_accumulation = config.get("gradient_accumulation", 1)
        
        # Mocks a GradScaler since we are simulating the framework
        # Only use amp in modern PyTorch versions, gracefully failing if not available
        try:
            self.scaler = torch.amp.GradScaler('cuda') if self.mixed_precision else None
        except Exception:
            self.scaler = None
            
    def clip_gradients(self, parameters) -> float:
        """Clips gradients and returns the global norm."""
        if self.gradient_clipping > 0.0:
            return torch.nn.utils.clip_grad_norm_(parameters, self.gradient_clipping)
        return 0.0
        
    def step(self, optimizer: torch.optim.Optimizer, parameters) -> None:
        """Performs a step combining scaling, clipping, and updating."""
        if self.scaler:
            self.scaler.unscale_(optimizer)
            self.clip_gradients(parameters)
            self.scaler.step(optimizer)
            self.scaler.update()
        else:
            self.clip_gradients(parameters)
            optimizer.step()
