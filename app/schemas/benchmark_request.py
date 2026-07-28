"""Benchmark Request Schema.

Author: DriftAdapt Contributors
Purpose: Defines the parameters for running a performance benchmark.
"""

import time
import uuid
from typing import Optional
from pydantic import BaseModel, Field


class BenchmarkRequest(BaseModel):
    """Payload for triggering a system performance benchmark."""
    
    benchmark_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this benchmark run")
    benchmark_type: str = Field(default="latency", description="Type of benchmark (e.g., 'latency', 'throughput', 'memory', 'all')")
    iterations: int = Field(default=10, ge=1, le=1000, description="Number of inference cycles to average over")
    batch_size: int = Field(default=1, ge=1, description="Concurrency/batching factor for the benchmark")
    adapter_id: Optional[str] = Field(default=None, description="Specific adapter to load for the benchmark")
    warmup_runs: int = Field(default=2, ge=0, description="Number of initial runs to discard from telemetry (to bypass cold starts)")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of request")
