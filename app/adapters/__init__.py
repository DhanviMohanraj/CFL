"""DriftAdapt Adapter Registry Package.

Author: DriftAdapt Contributors
Purpose: Manages clinic-owned LoRA adapters, tracking ownership, history, lookup, and activation.
"""

from app.adapters.adapter_info import AdapterInfo
from app.adapters.enums import AdapterStatus
from app.adapters.exceptions import (
    AdapterAlreadyExists,
    AdapterNotFound,
    ClinicNotFound,
    InvalidClinicID,
    RegistryPersistenceError,
)
from app.adapters.registry import AdapterRegistry

__all__ = [
    "AdapterInfo",
    "AdapterStatus",
    "AdapterRegistry",
    "AdapterAlreadyExists",
    "AdapterNotFound",
    "ClinicNotFound",
    "InvalidClinicID",
    "RegistryPersistenceError",
]
