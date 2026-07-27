"""DriftAdapt Federated Coordinator.

Author: DriftAdapt Contributors
"""

import time
from typing import List, Optional

from app.core.config.config_manager import ConfigManager
from app.core.logging.logger_factory import LoggerFactory
from app.core.metrics.metrics_bus import MetricsBus
from app.federated.communication.communication_manager import CommunicationManager
from app.federated.coordinator.client_selector import AllClientsStrategy, ClientSelectionStrategy, RandomSubsetStrategy
from app.federated.coordinator.coordinator_exceptions import CoordinatorFailure
from app.federated.coordinator.coordinator_metrics import CoordinatorMetrics
from app.federated.coordinator.coordinator_registry import CoordinatorRegistry
from app.federated.coordinator.failure_recovery import FailureRecovery
from app.federated.coordinator.participation_tracker import ParticipationTracker
from app.federated.coordinator.round_manager import RoundManager
from app.federated.coordinator.scheduler import Scheduler
from app.federated.coordinator.synchronization_barrier import SynchronizationBarrier
from app.federated.coordinator.timeout_manager import TimeoutManager


class FederatedCoordinator:
    """The central orchestrator of federated rounds."""
    
    def __init__(self, communication_manager: CommunicationManager, configs_dir: Optional[str] = None) -> None:
        self._logger = LoggerFactory.get_logger("FederatedCoordinator")
        
        # Core modules
        self._comm_manager = communication_manager
        
        config = ConfigManager(configs_dir).get_config()
        self._fed_config = getattr(config, "federation", None)
        
        self._min_clients = getattr(self._fed_config, "min_clients", 2) if self._fed_config else 2
        self._sync_timeout = getattr(self._fed_config, "synchronization_timeout", 60.0) if self._fed_config else 60.0
        allow_partial = getattr(self._fed_config, "allow_partial_participation", True) if self._fed_config else True
        strategy_name = getattr(self._fed_config, "client_selection_strategy", "all") if self._fed_config else "all"
        
        # Sub-components
        self._metrics_bus = MetricsBus()
        self._metrics = CoordinatorMetrics(self._metrics_bus)
        self._registry = CoordinatorRegistry()
        self._round_manager = RoundManager(self._registry)
        self._tracker = ParticipationTracker()
        self._barrier = SynchronizationBarrier()
        self._timeout_manager = TimeoutManager(self._metrics)
        self._recovery = FailureRecovery(allow_partial=allow_partial)
        self._scheduler = Scheduler()
        
        if strategy_name == "random":
            self._selector: ClientSelectionStrategy = RandomSubsetStrategy()
        else:
            self._selector = AllClientsStrategy()
            
    def initialize(self) -> None:
        self._logger.info("Federated Coordinator initialized.")
        
    def start_round(self, available_clients: List[str]) -> str:
        """Starts a communication round."""
        self._logger.info("Starting new communication round.")
        
        selected = self._selector.select(available_clients)
        if len(selected) < self._min_clients:
            self._logger.warning(f"Not enough clients selected ({len(selected)} < {self._min_clients}).")
            
        round_meta = self._round_manager.begin_round(selected)
        
        self._metrics.publish_round_started(round_meta.global_round, len(selected))
        self._barrier.reset()
        
        try:
            # Tell communication layer to broadcast sync requests
            self._comm_manager.synchronize(selected)
            
            # Wait for barrier (simulating waiting for uploads)
            # In a real environment, the communication layer receiving uploads would trigger `self._barrier.release()`
            self._barrier.wait_for_clients(timeout_seconds=self._sync_timeout)
            
            # Simulate marking clients as completed (in a real system, the communication layer does this via callbacks)
            for c in selected:
                self._tracker.record_completion(round_meta, c)
                
            if not self._recovery.can_proceed(round_meta, self._min_clients):
                self._round_manager.finish_round(success=False)
                self._metrics.publish_round_failed(round_meta.global_round, "Failure recovery rejected round.")
                return round_meta.round_id
                
            # Trigger Aggregation
            self._trigger_aggregation()
            
            self._round_manager.finish_round(success=True)
            self._metrics.publish_round_completed(
                round_meta.global_round,
                time.time() - round_meta.start_time,
                self._tracker.get_participation_rate(round_meta)
            )
            return round_meta.round_id
            
        except Exception as e:
            self._logger.error(f"Round {round_meta.global_round} failed: {e}")
            self._round_manager.finish_round(success=False)
            self._metrics.publish_round_failed(round_meta.global_round, str(e))
            raise CoordinatorFailure(f"Round failed: {e}") from e
            
    def _trigger_aggregation(self) -> None:
        self._logger.info("Triggering Merge Engine...")
        # Module 3.4 integration point
        start_time = time.time()
        # Mock aggregation delay
        time.sleep(0.01)
        self._metrics.publish_phase_duration("aggregation", time.time() - start_time)
        
    def complete_round(self) -> None:
        """Forces the current round to complete by releasing the barrier."""
        self._barrier.release()
        
    def cancel_round(self) -> None:
        self._barrier.abort()
        self._round_manager.finish_round(success=False)
        
    def shutdown(self) -> None:
        self._scheduler.cancel_all()
        self._logger.info("Coordinator shut down.")
        
    def status(self) -> str:
        curr = self._round_manager.current_round()
        return curr.status if curr else "IDLE"
