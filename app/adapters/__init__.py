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
    InvalidAdapterState,
    SerializationError,
    DeserializationError,
    ChecksumMismatch,
    ValidationFailed,
    UnsupportedFormat,
)
from app.adapters.registry import AdapterRegistry
from app.adapters.schemas import AdapterStateMetadata, ValidationReport
from app.adapters.metrics import AdapterMetricsPublisher
from app.adapters.checksum import ChecksumEngine
from app.adapters.validator import AdapterStateValidator
from app.adapters.serializer import AdapterSerializer
from app.adapters.state_utils import AdapterStateManager, calculate_size

__all__ = [
    "AdapterInfo",
    "AdapterStatus",
    "AdapterRegistry",
    "AdapterStateMetadata",
    "ValidationReport",
    "AdapterMetricsPublisher",
    "ChecksumEngine",
    "AdapterStateValidator",
    "AdapterSerializer",
    "AdapterStateManager",
    "calculate_size",
    "AdapterAlreadyExists",
    "AdapterNotFound",
    "ClinicNotFound",
    "InvalidClinicID",
    "RegistryPersistenceError",
    "InvalidAdapterState",
    "SerializationError",
    "DeserializationError",
    "ChecksumMismatch",
    "ValidationFailed",
    "UnsupportedFormat",
]
