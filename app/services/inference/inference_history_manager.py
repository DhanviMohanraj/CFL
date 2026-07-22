"""Inference History Manager Service.

Author: DriftAdapt Contributors
Purpose: Stores a permanent ledger of inference request metrics and resolutions.
"""

from typing import List, Optional
import hashlib

from app.core.logging import LoggerFactory
from app.schemas.inference_history import InferenceHistory
from app.schemas.inference_response import InferenceResponse
from app.schemas.token_usage import TokenUsage


class InferenceHistoryManager:
    """Manages the lifecycle and storage of immutable inference history records."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("InferenceHistoryManager")
        # In-memory store; in production, this pushes to a time-series DB like Prometheus or ELK.
        self._history: List[InferenceHistory] = []

    def _hash_prompt(self, prompt: str) -> str:
        """Hashes the raw prompt to avoid storing PII text in analytics."""
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def record_history(
        self,
        request_id: str,
        raw_prompt: str,
        response: InferenceResponse
    ) -> None:
        """Converts an inference response into a history record and archives it.
        
        Args:
            request_id: Originating request ID.
            raw_prompt: The raw user prompt (will be hashed).
            response: The finalized InferenceResponse object.
        """
        token_usage = TokenUsage(
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            estimated_cost=(response.total_tokens / 1000) * 0.0001, # Arbitrary LLM cost mock
            throughput=response.completion_tokens / response.inference_time if response.inference_time > 0 else 0.0
        )
        
        record = InferenceHistory(
            request_id=request_id,
            prompt_hash=self._hash_prompt(raw_prompt),
            adapter_used=response.adapter_used,
            latency=response.inference_time,
            token_usage=token_usage,
            response_length=len(response.generated_text),
            success=response.success
        )
        
        self._history.append(record)
        self._logger.debug(f"Recorded inference history for {request_id}.")

    def get_history(self, limit: int = 100) -> List[InferenceHistory]:
        """Retrieves recent inference records.
        
        Args:
            limit: Maximum number of records to return.
            
        Returns:
            List of InferenceHistory objects.
        """
        return self._history[-limit:]
