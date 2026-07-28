"""Throughput Benchmark Service.

Author: DriftAdapt Contributors
Purpose: Measures token generation speed over time.
"""

import time
from typing import Tuple, Optional

from app.core.logging import LoggerFactory
from app.services.inference.inference_engine import InferenceEngine
from app.schemas.inference_request import InferenceRequest


class ThroughputBenchmark:
    """Calculates tokens-per-second throughput under continuous load."""
    
    def __init__(self, inference_engine: InferenceEngine) -> None:
        self._logger = LoggerFactory.get_logger("ThroughputBenchmark")
        self._inference_engine = inference_engine

    def run_throughput_test(
        self,
        iterations: int,
        adapter_id: Optional[str] = None
    ) -> float:
        """Runs the throughput benchmark sequentially.
        
        Returns:
            Tokens per second (float)
        """
        self._logger.info(f"Starting throughput benchmark: {iterations} iterations.")
        
        total_tokens = 0
        total_time = 0.0
        
        req = InferenceRequest(
            prompt="Explain the benefits of privacy-preserving machine learning in a few paragraphs.",
            adapter_id=adapter_id,
            stream=False
        )
        req.generation_parameters.max_new_tokens = 100
        req.generation_parameters.do_sample = False
        
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                response = self._inference_engine.run_generation(req)
                elapsed = time.perf_counter() - start_time
                
                total_tokens += response.completion_tokens
                total_time += elapsed
                
            except Exception as e:
                self._logger.error(f"Throughput iteration {i} failed.", error=str(e))
                
        if total_time <= 0:
            return 0.0
            
        throughput = total_tokens / total_time
        self._logger.info(f"Throughput benchmark complete: {throughput:.2f} t/s")
        
        return throughput
