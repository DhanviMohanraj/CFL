"""DriftAdapt PEFT Integration Layer.

Author: DriftAdapt Contributors
Purpose: Exposes public interfaces for PEFT adapter lifecycle management and metadata tracking.
"""

from app.personalization.peft.peft_manager import PEFTManager
from app.personalization.peft.adapter_metadata import AdapterMetadata
from app.personalization.peft.peft_exceptions import (
    PEFTIntegrationError,
    AdapterInjectionError,
    TargetModuleNotFoundError,
    AdapterValidationError,
    FrozenModelViolationError
)

__all__ = [
    "PEFTManager",
    "AdapterMetadata",
    "PEFTIntegrationError",
    "AdapterInjectionError",
    "TargetModuleNotFoundError",
    "AdapterValidationError",
    "FrozenModelViolationError"
]
