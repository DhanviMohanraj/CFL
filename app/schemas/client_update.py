"""Client Update Schema for Federated Transmission.

Author: DriftAdapt Contributors
Purpose: Pydantic schemas for the complete payload of a federated update.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class ClientUpdate(BaseModel):
    """Structured update package containing the extracted state dict and integrity info."""
    
    client_id: str = Field(..., description="Unique identifier for the edge client")
    adapter_id: str = Field(..., description="Unique identifier for the adapter being updated")
    communication_round: int = Field(..., description="Current federated round")
    local_epoch: float = Field(..., description="Local epochs completed during personalization")
    adapter_version: str = Field(..., description="Version string for the adapter")
    update_timestamp: float = Field(..., description="Time when the update was packaged")
    lora_state_dict: Dict[str, Any] = Field(..., description="The minimal LoRA state dict (only trainable parameters)")
    trainable_parameter_count: int = Field(..., description="Total number of trainable parameters extracted")
    update_size: int = Field(..., description="Size of the update package in bytes")
    checksum: str = Field(..., description="SHA-256 or SHA-512 checksum of the state dict payload")
    compression_used: str = Field(..., description="Compression algorithm used (e.g., 'gzip', 'lzma', 'none')")
    encryption_used: str = Field(..., description="Encryption algorithm used (e.g., 'aes-256', 'none')")
