"""Latency Benchmark Service.

Author: DriftAdapt Contributors
Purpose: Measures end-to-end response latency for the inference engine.
"""

import time
import numpy as np
from typing import List, Tuple, Optional

from app.core.logging import LoggerFactory
from app.services.inference.inference_engine import InferenceEngine
from app.schemas.inference_request import InferenceRequest


class LatencyBenchmark:
    """Executes repeated generation queries to determine latency percentiles."""
    
    def __init__(self, inference_engine: InferenceEngine) -> None:
        self._logger = LoggerFactory.get_logger("LatencyBenchmark")
        self._inference_engine = inference_engine

    def run_latency_test(
        self,
        iterations: int,
        warmup_runs: int,
        adapter_id: Optional[str] = None
    ) -> Tuple[float, float, float]:
        """Runs the latency benchmark.
        
        Returns:
            Tuple of (avg_latency, min_latency, max_latency)
        """
        self._logger.info(f"Starting latency benchmark: {iterations} iterations, {warmup_runs} warmup.")
        
        latencies: List[float] = []
        
        req = InferenceRequest(
            prompt="Write a short summary about federated learning.",
            adapter_id=adapter_id,
            stream=False
        )
        # Fix generation to a deterministic length to measure raw inference latency 
        req.generation_parameters.max_new_tokens = 50
        req.generation_parameters.do_sample = False
        
        # Warmup phase (not recorded)
        for _ in range(warmup_runs):
            try:
                self._inference_engine.run_generation(req)
            except Exception as e:
                self._logger.warning(f"Warmup run failed: {e}")
                
        # Benchmark phase
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                self._inference_engine.run_generation(req)
                elapsed = time.perf_counter() - start_time
                latencies.append(elapsed)
            except Exception as e:
                self._logger.error(f"Iteration {i} failed.", error=str(e))
                
        if not latencies:
            return 0.0, 0.0, 0.0
            
        avg = float(np.mean(latencies))
        min_l = float(np.min(latencies))
        max_l = float(np.max(latencies))
        
        self._logger.info(f"Latency benchmark complete. Avg: {avg:.4f}s")
        return avg, min_l, max_l
