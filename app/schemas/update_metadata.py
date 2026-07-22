"""Update Metadata Schema for Federated Transmission.

Author: DriftAdapt Contributors
Purpose: Pydantic schemas for capturing device, model, and framework metadata associated with an update.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class UpdateMetadata(BaseModel):
    """Immutable metadata object capturing context for a federated update."""
    
    project_name: str = Field(..., description="Name of the project")
    foundation_model: str = Field(..., description="Name or identifier of the base model")
    adapter_name: str = Field(..., description="Name or identifier of the LoRA adapter")
    dataset_version: str = Field(..., description="Version of the local dataset used for training")
    training_duration: float = Field(..., description="Total training time in seconds")
    personalization_round: int = Field(..., description="The round of local personalization")
    software_version: str = Field(..., description="Version of the DriftAdapt platform")
    device_information: Dict[str, Any] = Field(..., description="Hardware specs and stats")
    framework_versions: Dict[str, str] = Field(..., description="Versions of PyTorch, Transformers, PEFT, etc.")
    timestamp: float = Field(..., description="Unix timestamp when this metadata was generated")
