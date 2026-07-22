"""Benchmark Result Schema.

Author: DriftAdapt Contributors
Purpose: Defines the output of a completed benchmark pass.
"""

import time
from typing import Optional
from pydantic import BaseModel, Field


class BenchmarkResult(BaseModel):
    """The final performance payload resulting from a benchmark run."""
    
    benchmark_id: str = Field(..., description="ID of the originating BenchmarkRequest")
    benchmark_type: str = Field(..., description="The type of benchmark that was executed")
    
    average_latency: float = Field(default=0.0, description="Mean latency per generation request (seconds)")
    minimum_latency: float = Field(default=0.0, description="Fastest request latency (seconds)")
    maximum_latency: float = Field(default=0.0, description="Slowest request latency (seconds)")
    
    throughput: float = Field(default=0.0, description="Overall throughput (e.g., tokens per second)")
    
    memory_usage: float = Field(default=0.0, description="Peak RAM usage during benchmark (MB)")
    cpu_usage: float = Field(default=0.0, description="Average CPU utilization percentage")
    gpu_usage: float = Field(default=0.0, description="Peak VRAM usage during benchmark (MB)")
    
    execution_time: float = Field(default=0.0, description="Total wall-clock time taken for the benchmark suite (seconds)")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of completion")
