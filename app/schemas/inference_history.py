"""Inference History Schema.

Author: DriftAdapt Contributors
Purpose: Represents a single immutable record of a completed inference request.
"""

from typing import Optional
from pydantic import BaseModel, Field
import time

from app.schemas.token_usage import TokenUsage


class InferenceHistory(BaseModel):
    """Immutable ledger record of an inference transaction."""
    
    request_id: str = Field(..., description="Correlates back to InferenceRequest.request_id")
    prompt_hash: str = Field(..., description="SHA-256 hash of the prompt for cache analytics without storing PII")
    adapter_used: Optional[str] = Field(default=None, description="Adapter ID used, or None for base model")
    latency: float = Field(..., description="Total time taken to fulfill the request (seconds)")
    token_usage: TokenUsage = Field(..., description="Token footprints")
    response_length: int = Field(default=0, description="Length of the raw generated string")
    success: bool = Field(default=True, description="Whether the request completed successfully")
    timestamp: float = Field(default_factory=time.time, description="Time the record was sealed")
