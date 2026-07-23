"""DriftAdapt Adapter Registry Info Model.

Author: DriftAdapt Contributors
Purpose: Strictly models structured adapter records using Pydantic validation.
"""

import time
import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.adapters.enums import AdapterStatus


class AdapterInfo(BaseModel):
    """Pydantic model representing metadata for a clinic-owned LoRA adapter."""

    adapter_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Globally unique identifier for the adapter."
    )
    clinic_id: str = Field(
        ...,
        description="The identifier of the clinic that owns this adapter."
    )
    adapter_name: str = Field(
        ...,
        description="The human-readable name of the adapter."
    )
    round_number: int = Field(
        ...,
        ge=1,
        description="The federated communication round when this adapter was created."
    )
    status: AdapterStatus = Field(
        default=AdapterStatus.REGISTERED,
        description="The current lifecycle status of the adapter."
    )
    created_at: float = Field(
        default_factory=time.time,
        description="POSIX epoch timestamp of when the adapter was registered."
    )
    updated_at: float = Field(
        default_factory=time.time,
        description="POSIX epoch timestamp of when the adapter was last modified."
    )
    is_active: bool = Field(
        default=False,
        description="Whether this adapter is currently the active one for the clinic."
    )
    checkpoint_path: Optional[str] = Field(
        default=None,
        description="The relative or absolute path to the saved adapter weights."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional unstructured dictionary containing additional metadata."
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional human-readable notes or description for this adapter."
    )

    @field_validator("clinic_id")
    @classmethod
    def validate_clinic_id(cls, v: str) -> str:
        """Ensures clinic ID is not empty or composed only of invalid characters."""
        if not v or not v.strip() or v == "None":
            raise ValueError("clinic_id cannot be empty or 'None'.")
        # Ensure only alphanumeric and underscores
        if not v.replace("_", "").isalnum():
            raise ValueError("clinic_id must contain only alphanumeric characters and underscores.")
        return v
    
    @model_validator(mode="after")
    def sync_active_status(self) -> "AdapterInfo":
        """Ensures `is_active` boolean matches `status` enum."""
        if self.status == AdapterStatus.ACTIVE:
            self.is_active = True
        elif self.is_active:
            # If is_active is True but status isn't ACTIVE, update status
            if self.status != AdapterStatus.DELETED:
                self.status = AdapterStatus.ACTIVE
        else:
            self.is_active = False
        return self
