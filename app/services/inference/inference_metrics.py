"""Inference Metrics Service.

Author: DriftAdapt Contributors
Purpose: Computes inference statistics and dispatches them to the centralized telemetry bus.
"""

from typing import Dict, Any

from app.core.logging import LoggerFactory
from app.schemas.inference_statistics import InferenceStatistics
from app.schemas.inference_history import InferenceHistory


class InferenceMetrics:
    """Calculates and maintains running node-level statistics for the inference engine."""
    
    def __init__(self, metrics_bus: Any = None) -> None:
        self._logger = LoggerFactory.get_logger("InferenceMetrics")
        # Optional integration with centralized MetricsBus
        self._metrics_bus = metrics_bus
        
        self._total_requests: int = 0
        self._successful_requests: int = 0
        self._failed_requests: int = 0
        self._streaming_requests: int = 0
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        
        self._total_latency: float = 0.0
        self._total_tokens: int = 0

    def record_success(self, latency: float, total_tokens: int, streaming: bool = False) -> None:
        """Records a successful generation run."""
        self._total_requests += 1
        self._successful_requests += 1
        self._total_latency += latency
        self._total_tokens += total_tokens
        if streaming:
            self._streaming_requests += 1
            
        if self._metrics_bus and hasattr(self._metrics_bus, "record"):
            self._metrics_bus.record("inference.requests", 1)
            self._metrics_bus.record("inference.success", 1)
            self._metrics_bus.record("inference.latency_ms", latency * 1000)
            self._metrics_bus.record("inference.tokens_generated", total_tokens)

    def record_failure(self) -> None:
        """Records a failed generation run."""
        self._total_requests += 1
        self._failed_requests += 1
        
        if self._metrics_bus and hasattr(self._metrics_bus, "record"):
            self._metrics_bus.record("inference.requests", 1)
            self._metrics_bus.record("inference.failures", 1)

    def record_cache_hit(self) -> None:
        """Records an exact match cache hit."""
        self._cache_hits += 1
        
        if self._metrics_bus and hasattr(self._metrics_bus, "record"):
            self._metrics_bus.record("inference.cache_hits", 1)

    def record_cache_miss(self) -> None:
        """Records a cache miss."""
        self._cache_misses += 1
        
        if self._metrics_bus and hasattr(self._metrics_bus, "record"):
            self._metrics_bus.record("inference.cache_misses", 1)

    def get_statistics(self, active_adapter_count: int = 0) -> InferenceStatistics:
        """Compiles running metrics into the standard schema."""
        avg_latency = self._total_latency / self._successful_requests if self._successful_requests > 0 else 0.0
        avg_tokens = self._total_tokens / self._successful_requests if self._successful_requests > 0 else 0.0
        
        stats = InferenceStatistics(
            total_requests=self._total_requests,
            successful_requests=self._successful_requests,
            failed_requests=self._failed_requests,
            average_latency=avg_latency,
            average_token_usage=avg_tokens,
            streaming_requests=self._streaming_requests,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            active_adapter_count=active_adapter_count
        )
        return stats
