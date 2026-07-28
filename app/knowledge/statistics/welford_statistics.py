"""DriftAdapt Welford Statistics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any


class WelfordStatistics:
    """Computes online mean and variance using Welford's algorithm."""
    
    def __init__(self) -> None:
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0
        
    def update(self, value: float) -> None:
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        self.m2 += delta * delta2
        
    def variance(self) -> float:
        if self.count < 2:
            return 0.0
        return self.m2 / (self.count - 1)
