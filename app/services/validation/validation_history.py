"""Validation History Service.

Author: DriftAdapt Contributors
Purpose: Stores a permanent ledger of past validation and benchmark sweeps.
"""

from typing import List, Dict, Any

from app.core.logging import LoggerFactory
from app.schemas.validation_result import ValidationResult
from app.schemas.benchmark_result import BenchmarkResult


class ValidationHistory:
    """Manages the lifecycle and storage of historical QA and perf runs."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("ValidationHistory")
        self._validations: List[ValidationResult] = []
        self._benchmarks: List[BenchmarkResult] = []

    def record_validation(self, result: ValidationResult) -> None:
        """Archives a completed validation sweep."""
        self._validations.append(result)
        self._logger.debug(f"Recorded validation history for {result.validation_id}")

    def record_benchmark(self, result: BenchmarkResult) -> None:
        """Archives a completed benchmark sweep."""
        self._benchmarks.append(result)
        self._logger.debug(f"Recorded benchmark history for {result.benchmark_id}")

    def get_recent_validations(self, limit: int = 50) -> List[ValidationResult]:
        """Returns the most recent validation results."""
        return self._validations[-limit:]

    def get_recent_benchmarks(self, limit: int = 50) -> List[BenchmarkResult]:
        """Returns the most recent benchmark results."""
        return self._benchmarks[-limit:]
