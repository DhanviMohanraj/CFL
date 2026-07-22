"""Integrity Report Schema for Federated Updates.

Author: DriftAdapt Contributors
Purpose: Schema for documenting the integrity verification of a federated update payload.
"""

from pydantic import BaseModel, Field


class IntegrityReport(BaseModel):
    """Integrity verification results for an update payload."""
    
    checksum: str = Field(..., description="The computed hash string")
    hash_algorithm: str = Field(..., description="Algorithm used (e.g., 'SHA-256')")
    validation_status: bool = Field(..., description="True if the checksum matches the expected value")
    corruption_detected: bool = Field(..., description="True if payload corruption or tampering was detected")
    verification_timestamp: float = Field(..., description="Time when the integrity check was performed")
