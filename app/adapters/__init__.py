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
    VersionAlreadyExists,
    VersionNotFound,
    RollbackFailed,
    InvalidVersion,
    ChecksumValidationFailed,
    PolicyViolation,
    InvalidStateTransition,
)
from app.adapters.merge_exceptions import (
    MergeFailed,
    IncompatibleAdapters,
    InvalidMergeStrategy,
    TensorShapeMismatch,
    DuplicateAdapterError,
    EmptyMergeInput,
)
from app.adapters.registry import AdapterRegistry
from app.adapters.schemas import AdapterStateMetadata, ValidationReport
from app.adapters.metrics import AdapterMetricsPublisher
from app.adapters.checksum import ChecksumEngine
from app.adapters.validator import AdapterStateValidator
from app.adapters.serializer import AdapterSerializer
from app.adapters.state_utils import AdapterStateManager, calculate_size
from app.adapters.version_metadata import AdapterVersionMetadata
from app.adapters.lifecycle import VersionLifecycleManager, VersionState
from app.adapters.version_manager import AdapterVersionManager
from app.adapters.version_policy import VersionPolicyManager
from app.adapters.version_storage import VersionStorage
from app.adapters.version_history import VersionHistoryManager
from app.adapters.rollback import RollbackEngine

from app.adapters.merge_metadata import AdapterMergeMetadata
from app.adapters.merge_metrics import MergeMetricsPublisher
from app.adapters.compatibility import CompatibilityChecker
from app.adapters.merge_validator import MergeValidator
from app.adapters.merge_strategy import AdapterMergeStrategy
from app.adapters.averaging import NaiveAverageMerge
from app.adapters.merge_engine import AdapterMergeEngine

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
    "AdapterVersionMetadata",
    "VersionLifecycleManager",
    "VersionState",
    "AdapterVersionManager",
    "VersionPolicyManager",
    "VersionStorage",
    "VersionHistoryManager",
    "RollbackEngine",
    "AdapterMergeMetadata",
    "MergeMetricsPublisher",
    "CompatibilityChecker",
    "MergeValidator",
    "AdapterMergeStrategy",
    "NaiveAverageMerge",
    "AdapterMergeEngine",
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
    "VersionAlreadyExists",
    "VersionNotFound",
    "RollbackFailed",
    "InvalidVersion",
    "ChecksumValidationFailed",
    "PolicyViolation",
    "InvalidStateTransition",
    "MergeFailed",
    "IncompatibleAdapters",
    "InvalidMergeStrategy",
    "TensorShapeMismatch",
    "DuplicateAdapterError",
    "EmptyMergeInput",
]
