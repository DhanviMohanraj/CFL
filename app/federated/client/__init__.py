"""DriftAdapt Federated Client Module.

Author: DriftAdapt Contributors
"""

from app.federated.client.client_exceptions import (
    ClientRuntimeError,
    TrainingSessionError,
    CheckpointError,
    ClientRegistrationError,
    RuntimeStateError,
    TrainingInterruptedError,
)

from app.federated.client.client_schema import (
    TrainingEpochResult,
    ClientIdentity,
    CheckpointMetadata,
)

from app.federated.client.runtime_state import RuntimeState
from app.federated.client.client_session import ClientSession
from app.federated.client.training_history import TrainingHistory
from app.federated.client.checkpoint_scheduler import CheckpointScheduler
from app.federated.client.local_training_manager import LocalTrainingManager
from app.federated.client.training_orchestrator import TrainingOrchestrator
from app.federated.client.client_registry import ClientRegistry
from app.federated.client.client_runtime import ClientRuntime
from app.federated.client.client_manager import ClientManager

__all__ = [
    "ClientRuntimeError",
    "TrainingSessionError",
    "CheckpointError",
    "ClientRegistrationError",
    "RuntimeStateError",
    "TrainingInterruptedError",
    "TrainingEpochResult",
    "ClientIdentity",
    "CheckpointMetadata",
    "RuntimeState",
    "ClientSession",
    "TrainingHistory",
    "CheckpointScheduler",
    "LocalTrainingManager",
    "TrainingOrchestrator",
    "ClientRegistry",
    "ClientRuntime",
    "ClientManager",
]
