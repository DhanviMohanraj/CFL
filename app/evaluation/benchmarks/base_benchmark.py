"""DriftAdapt Base Benchmark.

Author: DriftAdapt Contributors
"""

import abc
from typing import Dict, Any


class BaseBenchmark(abc.ABC):
    """Base class for all benchmarks."""
    
    @abc.abstractmethod
    def evaluate(self, model: Any, config: Dict[str, Any]) -> Dict[str, float]:
        pass
