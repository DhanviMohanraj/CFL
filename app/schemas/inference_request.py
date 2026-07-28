"""Inference Request Schema.

Author: DriftAdapt Contributors
Purpose: Defines the structure of an incoming inference API request.
"""

from typing import Optional
from pydantic import BaseModel, Field
import uuid
import time

from app.schemas.generation_parameters import GenerationParameters


class InferenceRequest(BaseModel):
    """The payload structure for requesting personalized text generation."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the request")
    prompt: str = Field(..., description="The main user input text")
    system_prompt: Optional[str] = Field(default=None, description="Optional system-level instructions")
    adapter_id: Optional[str] = Field(default=None, description="The specific LoRA adapter to load/use. None means base model only.")
    adapter_version: Optional[str] = Field(default=None, description="Specific version of the adapter to use")
    conversation_id: Optional[str] = Field(default=None, description="For grouping multiple turns in analytics")
    generation_parameters: GenerationParameters = Field(default_factory=GenerationParameters, description="Generation behavior overrides")
    stream: bool = Field(default=False, description="Whether to stream the response via Server-Sent Events (SSE)")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of the request origin")
