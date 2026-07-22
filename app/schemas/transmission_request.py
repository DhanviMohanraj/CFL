"""Transmission Request Schema for Federated Updates.

Author: DriftAdapt Contributors
Purpose: Schema for requesting the transmission of a federated update payload to a remote server.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class TransmissionRequest(BaseModel):
    """Configuration and payload request for securely uploading an update package."""
    
    destination_server: str = Field(..., description="The fully qualified URL or address of the aggregation server")
    update_package: bytes = Field(..., description="The fully prepared, compressed, and encrypted payload")
    priority: int = Field(default=1, description="Upload priority (lower is higher priority)")
    retry_limit: int = Field(default=3, description="Maximum number of retry attempts for network failures")
    timeout: float = Field(default=30.0, description="Network timeout in seconds per attempt")
    compression: str = Field(default="zstd", description="Compression algorithm used (e.g., 'gzip', 'lzma', 'zstd')")
    encryption: str = Field(default="aes-256", description="Encryption algorithm used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata payload")
