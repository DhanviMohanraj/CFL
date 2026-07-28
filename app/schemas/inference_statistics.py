"""Inference Statistics Schema.

Author: DriftAdapt Contributors
Purpose: Aggregated metrics for overall system health and throughput.
"""

from pydantic import BaseModel, Field


class InferenceStatistics(BaseModel):
    """Global node-level statistics for inference workloads."""
    
    total_requests: int = Field(default=0, description="Total number of inference requests handled")
    successful_requests: int = Field(default=0, description="Number of successfully completed requests")
    failed_requests: int = Field(default=0, description="Number of requests that ended in error")
    average_latency: float = Field(default=0.0, description="Moving average latency in seconds")
    average_token_usage: float = Field(default=0.0, description="Moving average total tokens per request")
    streaming_requests: int = Field(default=0, description="Count of requests using SSE streaming")
    cache_hits: int = Field(default=0, description="Number of times exact prompts were resolved from cache")
    cache_misses: int = Field(default=0, description="Number of times prompts required full generation")
    active_adapter_count: int = Field(default=0, description="Current number of LoRA adapters loaded in VRAM/RAM")
