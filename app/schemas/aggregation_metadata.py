"""Aggregation Metadata Schema.

Author: DriftAdapt Contributors
Purpose: Defines the environment context for a completed global adapter merge.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class AggregationMetadata(BaseModel):
    """Contextual metadata surrounding an aggregation round."""
    
    foundation_model_version: str = Field(..., description="The base LLM ID (e.g., Qwen/Qwen2.5-3B-Instruct)")
    server_environment: str = Field(..., description="OS or runtime info where aggregation occurred")
    torch_version: str = Field(..., description="PyTorch version used for the merge")
    total_participating_clients: int = Field(default=0, description="Total number of clients ever seen by the aggregator")
    global_dataset_size_accumulated: int = Field(default=0, description="Sum of dataset sizes from all contributors")
    framework_versions: Dict[str, str] = Field(default_factory=dict, description="Versions of peft, transformers, etc.")
