"""DriftAdapt Model Metadata Schema Module.

Author: DriftAdapt Contributors
Purpose: Defines Pydantic data model representing detailed foundation model metadata.
Future Integration: Exported by ModelManager and queried by downstream modules.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    """Metadata specifications for a loaded foundation language model."""

    model_name: str = Field(..., description="HuggingFace model identifier or local directory path.")
    architecture: str = Field(default="CausalLM", description="Model architecture type.")
    parameter_count: int = Field(default=0, description="Total number of parameters in the model.")
    trainable_parameters: int = Field(default=0, description="Total trainable parameters (should be 0 for base).")
    tokenizer_name: str = Field(..., description="Tokenizer identifier or path.")
    vocab_size: int = Field(default=0, description="Tokenizer vocabulary size.")
    context_length: int = Field(default=2048, description="Maximum sequence length context window.")
    hidden_size: int = Field(default=0, description="Model hidden layer dimension size.")
    quantization_mode: str = Field(default="none", description="Quantization mode (e.g. 4bit, 8bit, none).")
    precision: str = Field(default="float32", description="PyTorch tensor float precision (e.g. float16, bfloat16).")
    device: str = Field(default="cpu", description="Execution device where model resides (e.g. cpu, cuda:0).")
    memory_footprint_mb: float = Field(default=0.0, description="VRAM / RAM memory occupied by model parameters in MB.")
    load_time_seconds: float = Field(default=0.0, description="Time taken to load model into memory in seconds.")
    disk_size_mb: float = Field(default=0.0, description="Size of weight files on disk in MB.")
    checkpoint_location: str = Field(default="", description="Path to checkpoint / cache location on filesystem.")
    is_frozen: bool = Field(default=True, description="True if all parameters have requires_grad set to False.")
