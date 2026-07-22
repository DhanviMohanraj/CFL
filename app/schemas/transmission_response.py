"""Transmission Response Schema for Federated Updates.

Author: DriftAdapt Contributors
Purpose: Schema for representing the outcome of an update transmission.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TransmissionResponse(BaseModel):
    """Outcome and statistics of a transmission request."""
    
    success: bool = Field(..., description="Whether the transmission was ultimately successful")
    upload_duration: float = Field(..., description="Total time taken to upload the payload in seconds")
    bytes_transferred: int = Field(..., description="Total bytes successfully sent over the wire")
    server_acknowledgement: bool = Field(..., description="Whether the server explicitly acknowledged receipt")
    checksum_verified: bool = Field(..., description="Whether the server verified the payload checksum")
    retry_count: int = Field(..., description="Number of retries that occurred during transmission")
    transmission_status: str = Field(..., description="Status string (e.g., 'SUCCESS', 'FAILED_TIMEOUT', 'FAILED_CHECKSUM')")
    error_message: Optional[str] = Field(None, description="Detailed error message if the transmission failed")
