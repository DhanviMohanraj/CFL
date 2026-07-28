"""Validation Summary Schema.

Author: DriftAdapt Contributors
Purpose: Aggregated statistics of multiple validation runs over time.
"""

from pydantic import BaseModel, Field


class ValidationSummary(BaseModel):
    """Cumulative historical record of the node's validation lifecycle."""
    
    total_validations: int = Field(default=0, description="Total validation sweeps executed")
    successful_validations: int = Field(default=0, description="Number of sweeps that passed all checks")
    failed_validations: int = Field(default=0, description="Number of sweeps that encountered a critical failure")
    benchmark_runs: int = Field(default=0, description="Number of performance benchmarks executed")
    
    average_validation_time: float = Field(default=0.0, description="Average time taken per validation sweep (seconds)")
    system_health_score: float = Field(default=100.0, description="Heuristic score (0-100) representing overall node health")
