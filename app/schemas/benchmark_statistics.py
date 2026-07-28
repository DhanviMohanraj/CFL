"""Benchmark Statistics Schema.

Author: DriftAdapt Contributors
Purpose: Contains aggregated historical analysis of benchmark results.
"""

from pydantic import BaseModel, Field


class BenchmarkStatistics(BaseModel):
    """Historical aggregations of benchmarking metrics."""
    
    total_benchmarks: int = Field(default=0, description="Total benchmarks run over the lifetime of the node")
    
    global_average_latency: float = Field(default=0.0, description="Historical average generation latency")
    global_average_throughput: float = Field(default=0.0, description="Historical average tokens per second")
    
    peak_memory_observed: float = Field(default=0.0, description="Highest RAM usage observed (MB)")
    peak_vram_observed: float = Field(default=0.0, description="Highest VRAM usage observed (MB)")
