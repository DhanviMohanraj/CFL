"""Tests for Gradient Manager.

Author: DriftAdapt Contributors
"""

import torch
import torch.nn as nn

from app.training.gradient_manager import GradientManager


def test_gradient_manager():
    mgr = GradientManager({"gradient_clipping": 1.0, "mixed_precision": False})
    
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = nn.Linear(10, 10)
            
    model = DummyModel()
    outputs = model(torch.randn(1, 10))
    loss = outputs.sum()
    loss.backward()
    
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    
    mgr.step(optimizer, model.parameters())
