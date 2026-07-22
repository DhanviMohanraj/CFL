"""Validation Registry Service.

Author: DriftAdapt Contributors
Purpose: In-memory tracker for actively running validation and benchmark tasks.
"""

import time
from typing import Dict, Any, Optional

from app.core.logging import LoggerFactory


class ValidationRegistry:
    """Tracks active long-running QA operations to prevent overlapping conflicts."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("ValidationRegistry")
        self._active_validations: Dict[str, float] = {}
        self._active_benchmarks: Dict[str, float] = {}

    def register_validation(self, validation_id: str) -> None:
        self._active_validations[validation_id] = time.time()
        
    def unregister_validation(self, validation_id: str) -> None:
        if validation_id in self._active_validations:
            del self._active_validations[validation_id]

    def register_benchmark(self, benchmark_id: str) -> None:
        self._active_benchmarks[benchmark_id] = time.time()
        
    def unregister_benchmark(self, benchmark_id: str) -> None:
        if benchmark_id in self._active_benchmarks:
            del self._active_benchmarks[benchmark_id]

    def is_validation_running(self) -> bool:
        return len(self._active_validations) > 0

    def is_benchmark_running(self) -> bool:
        return len(self._active_benchmarks) > 0
