"""Response Formatter Service.

Author: DriftAdapt Contributors
Purpose: Maps raw generation texts and metadata into standardized API responses.
"""

from typing import Dict, Any, Optional

from app.core.logging import LoggerFactory
from app.schemas.inference_response import InferenceResponse
from app.schemas.inference_request import InferenceRequest
from app.schemas.token_usage import TokenUsage


class ResponseFormatter:
    """Prepares and structures final inference output responses."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("ResponseFormatter")

    def format_response(
        self,
        request: InferenceRequest,
        generated_text: str,
        latency_s: float,
        prompt_tokens: int,
        completion_tokens: int,
        active_adapter: Optional[str]
    ) -> InferenceResponse:
        """Constructs an InferenceResponse model from raw components.
        
        Args:
            request: The original client InferenceRequest.
            generated_text: The raw LLM generation string.
            latency_s: Measured time for generation.
            prompt_tokens: Tokens in input prompt.
            completion_tokens: Tokens generated.
            active_adapter: The ID of the currently attached adapter.
            
        Returns:
            A compliant InferenceResponse object.
        """
        total_tokens = prompt_tokens + completion_tokens
        
        response = InferenceResponse(
            success=True,
            generated_text=generated_text,
            adapter_used=active_adapter,
            inference_time=latency_s,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            generation_parameters=request.generation_parameters.model_dump(),
            finish_reason="stop" # Simple heuristic; actual HF generation config could provide this
        )
        
        self._logger.debug(f"Formatted response for request {request.request_id} ({total_tokens} total tokens in {latency_s:.2f}s).")
        return response
