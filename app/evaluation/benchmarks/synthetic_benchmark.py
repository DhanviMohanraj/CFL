"""DriftAdapt Synthetic Benchmark.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.evaluation.benchmarks.base_benchmark import BaseBenchmark


class SyntheticBenchmark(BaseBenchmark):
    """Synthetic clinic benchmark evaluator."""
    
    def evaluate(self, model: Any, config: Dict[str, Any]) -> Dict[str, float]:
        return {"accuracy": 0.0}
