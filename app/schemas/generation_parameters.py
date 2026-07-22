"""Generation Parameters Schema.

Author: DriftAdapt Contributors
Purpose: Defines the configurable parameters for LLM text generation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class GenerationParameters(BaseModel):
    """Parameters passed to the underlying HuggingFace generate() call."""
    
    max_new_tokens: int = Field(default=256, ge=1, le=8192, description="Maximum number of new tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, description="Sampling temperature (higher is more random)")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling probability")
    top_k: int = Field(default=50, ge=0, description="Top-k sampling threshold")
    repetition_penalty: float = Field(default=1.1, ge=1.0, description="Penalty for repeating tokens")
    do_sample: bool = Field(default=True, description="Whether to use sampling or greedy decoding")
    num_beams: int = Field(default=1, ge=1, description="Number of beams for beam search")
    early_stopping: bool = Field(default=False, description="Whether to stop generation when all beams reach EOS")
    stop_sequences: List[str] = Field(default_factory=list, description="Custom string sequences that halt generation")
    seed: Optional[int] = Field(default=None, description="Random seed for deterministic generation")
    return_full_text: bool = Field(default=False, description="Whether to include the prompt in the output text")
