"""DriftAdapt Federated Coordinator Module.

Author: DriftAdapt Contributors
"""

from app.federated.coordinator.coordinator_exceptions import (
    CoordinatorError,
    RoundInitializationError,
    ClientSelectionError,
    SynchronizationTimeout,
    AggregationTriggerError,
    CoordinatorFailure,
    RoundRecoveryError,
)

from app.federated.coordinator.coordinator_schema import (
    FederatedRoundMetadata,
    CoordinatorStatistics,
)

from app.federated.coordinator.coordinator_metrics import CoordinatorMetrics
from app.federated.coordinator.coordinator_registry import CoordinatorRegistry
from app.federated.coordinator.participation_tracker import ParticipationTracker
from app.federated.coordinator.client_selector import (
    ClientSelectionStrategy,
    AllClientsStrategy,
    RandomSubsetStrategy,
    PercentageParticipationStrategy,
)
from app.federated.coordinator.synchronization_barrier import SynchronizationBarrier
from app.federated.coordinator.timeout_manager import TimeoutManager
from app.federated.coordinator.failure_recovery import FailureRecovery
from app.federated.coordinator.round_manager import RoundManager
from app.federated.coordinator.scheduler import Scheduler
from app.federated.coordinator.coordinator import FederatedCoordinator


__all__ = [
    "CoordinatorError",
    "RoundInitializationError",
    "ClientSelectionError",
    "SynchronizationTimeout",
    "AggregationTriggerError",
    "CoordinatorFailure",
    "RoundRecoveryError",
    "FederatedRoundMetadata",
    "CoordinatorStatistics",
    "CoordinatorMetrics",
    "CoordinatorRegistry",
    "ParticipationTracker",
    "ClientSelectionStrategy",
    "AllClientsStrategy",
    "RandomSubsetStrategy",
    "PercentageParticipationStrategy",
    "SynchronizationBarrier",
    "TimeoutManager",
    "FailureRecovery",
    "RoundManager",
    "Scheduler",
    "FederatedCoordinator",
]
