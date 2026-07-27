"""DriftAdapt Communication Schema.

Author: DriftAdapt Contributors
Purpose: Defines Pydantic models for communication data structures.
"""

import time
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AdapterTransmission(BaseModel):
    """Metadata regarding a transmitted adapter package."""
    adapter_id: str = Field(..., description="Base adapter ID.")
    version_id: str = Field(..., description="Adapter version ID.")
    clinic_id: str = Field(..., description="Clinic ID originating or receiving the transmission.")
    session_id: str = Field(..., description="Communication session ID.")
    communication_round: int = Field(..., description="Federated round.")
    package_size: int = Field(..., description="Total size of the package in bytes.")
    checksum: str = Field(..., description="Cryptographic checksum of the package.")
    compression: bool = Field(..., description="Whether the payload is compressed.")
    created_at: float = Field(default_factory=time.time, description="Timestamp of package creation.")


class CommunicationMessage(BaseModel):
    """A standard message envelope for all federated communication."""
    message_id: str = Field(..., description="Unique ID for this message.")
    sender: str = Field(..., description="Sender ID (e.g., clinic_id or 'coordinator').")
    receiver: str = Field(..., description="Receiver ID.")
    message_type: str = Field(..., description="Type of message (REGISTER, UPLOAD, DOWNLOAD, etc.).")
    timestamp: float = Field(default_factory=time.time, description="Creation timestamp.")
    payload: Optional[bytes] = Field(None, description="Binary payload, e.g., adapter weights.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary message metadata.")
    priority: int = Field(default=0, description="Message priority (higher is more urgent).")
    status: str = Field(default="PENDING", description="Current status of the message.")


class SynchronizationStatus(BaseModel):
    """State tracking for a synchronization session."""
    session_id: str = Field(..., description="Unique synchronization session ID.")
    current_state: str = Field(default="INIT", description="Current state of sync.")
    upload_complete: bool = Field(default=False, description="Whether upload is done.")
    download_complete: bool = Field(default=False, description="Whether download is done.")
    verified: bool = Field(default=False, description="Whether synchronization was verified securely.")
    last_updated: float = Field(default_factory=time.time, description="Last status update timestamp.")
    retry_count: int = Field(default=0, description="Number of times sync was retried.")
