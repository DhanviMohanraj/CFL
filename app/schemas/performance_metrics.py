"""Performance Metrics Schema.

Author: DriftAdapt Contributors
Purpose: Stores low-level telemetry for a specific benchmarking interval.
"""

from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    """Granular performance indicators captured during an active workload."""
    
    latency: float = Field(default=0.0, description="Average response latency (seconds)")
    throughput: float = Field(default=0.0, description="Overall throughput")
    requests_per_second: float = Field(default=0.0, description="API requests handled per second")
    tokens_per_second: float = Field(default=0.0, description="Total generation tokens emitted per second")
    
    adapter_loading_time: float = Field(default=0.0, description="Time taken to map PEFT adapter weights into memory (seconds)")
    model_loading_time: float = Field(default=0.0, description="Time taken to load base model (seconds)")
    inference_time: float = Field(default=0.0, description="Time taken strictly in model.generate() (seconds)")
    
    memory_consumption: float = Field(default=0.0, description="System RAM usage (MB)")
    gpu_memory: float = Field(default=0.0, description="Allocated VRAM (MB)")
    cpu_utilization: float = Field(default=0.0, description="CPU usage percentage")
