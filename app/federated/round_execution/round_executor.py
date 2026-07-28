"""DriftAdapt Round Executor.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any

from app.core.metrics.metrics_bus import MetricsBus
from app.federated.round_execution.round_manager import RoundManager
from app.federated.round_execution.client_dispatcher import ClientDispatcher
from app.federated.round_execution.adapter_collector import AdapterCollector
from app.federated.round_execution.adapter_validator import AdapterValidator
from app.federated.round_execution.aggregation_trigger import AggregationTrigger
from app.federated.round_execution.redistribution_manager import RedistributionManager
from app.federated.round_execution.synchronization_controller import SynchronizationController
from app.federated.round_execution.execution_scheduler import ExecutionScheduler
from app.federated.round_execution.round_state_machine import RoundStateMachine, RoundState
from app.federated.round_execution.execution_history import ExecutionHistory
from app.federated.round_execution.round_registry import RoundRegistry
from app.federated.round_execution.execution_metrics import ExecutionMetrics
from app.federated.round_execution.execution_logger import ExecutionLogger
from app.federated.round_execution.execution_validator import ExecutionValidator
from app.federated.round_execution.execution_checkpoint import ExecutionCheckpoint
from app.federated.round_execution.execution_exceptions import ExecutionError


class FederatedRoundExecutor:
    """Executes a single federated learning round."""
    
    def __init__(self, config: Dict[str, Any], metrics_bus: MetricsBus) -> None:
        self.config = config
        
        self.registry = RoundRegistry()
        self.manager = RoundManager(self.registry)
        
        self.state_machine = RoundStateMachine()
        self.history = ExecutionHistory()
        self.metrics = ExecutionMetrics(metrics_bus)
        
        self.dispatcher = ClientDispatcher()
        self.collector = AdapterCollector()
        self.validator = AdapterValidator()
        self.aggregator = AggregationTrigger()
        self.redistributor = RedistributionManager()
        
        self.execution_scheduler = ExecutionScheduler(config.get("retry_attempts", 3))
        self.execution_validator = ExecutionValidator()
        self.checkpoint = ExecutionCheckpoint()
        
        self.round_id = None
        self.logger = None
        
    def initialize(self, month: int, epoch: int, clients: List[str]) -> str:
        """Initializes the round."""
        self.execution_validator.validate_round_config(self.config)
        self.execution_validator.validate_clients(clients)
        
        self.round_id = self.manager.start_round(month, epoch, clients)
        self.logger = ExecutionLogger(self.round_id)
        
        self.state_machine.transition_to(RoundState.PREPARING)
        self.history.record_event("ROUND_INITIALIZED", {"month": month, "clients": clients})
        self.metrics.publish_event("round.started", {"round_id": self.round_id})
        
        self.logger.info(f"Round {self.round_id} initialized.")
        return self.round_id
        
    def execute(self, clients: List[str], month: int) -> None:
        """Executes the complete round workflow."""
        try:
            self.state_machine.transition_to(RoundState.DISPATCHING)
            self.dispatcher.dispatch(clients, month, self.config)
            self.metrics.publish_event("training.dispatched")
            
            self.state_machine.transition_to(RoundState.TRAINING)
            self.metrics.publish_event("training.completed")
            
            self.state_machine.transition_to(RoundState.COLLECTING)
            adapters = self.collector.collect_adapters(clients)
            self.metrics.publish_event("adapter.received")
            
            self.state_machine.transition_to(RoundState.VALIDATING)
            valid_adapters = []
            for path, meta in adapters:
                if self.validator.validate(path, meta):
                    valid_adapters.append(path)
            self.metrics.publish_event("adapter.validated")
            
            if self.config.get("checkpoint_before_aggregation", True):
                self.checkpoint.save_checkpoint(self.round_id, "pre_aggregation", {})
                
            self.state_machine.transition_to(RoundState.AGGREGATING)
            global_adapter = self.aggregator.trigger_aggregation(self.round_id, valid_adapters)
            self.metrics.publish_event("aggregation.completed")
            
            self.state_machine.transition_to(RoundState.REDISTRIBUTING)
            self.redistributor.redistribute(global_adapter, clients)
            self.metrics.publish_event("redistribution.completed")
            
            if self.config.get("checkpoint_after_round", True):
                self.checkpoint.save_checkpoint(self.round_id, "post_round", {})
                
            self.state_machine.transition_to(RoundState.COMPLETED)
            self.manager.finish_round(self.round_id, success=True)
            self.metrics.publish_event("round.completed")
            self.logger.info("Round completed successfully.")
            
        except Exception as e:
            self.state_machine.transition_to(RoundState.FAILED)
            self.manager.finish_round(self.round_id, success=False)
            self.metrics.publish_event("round.failed")
            self.logger.error(f"Round failed: {e}")
            raise ExecutionError(f"Round execution failed: {e}") from e
            
    def pause(self) -> None:
        self.state_machine.transition_to(RoundState.PAUSED)
        
    def resume(self) -> None:
        self.state_machine.transition_to(RoundState.PREPARING)
        
    def stop(self) -> None:
        self.state_machine.transition_to(RoundState.CANCELLED)
        if self.round_id:
            self.manager.cancel_round(self.round_id)
            
    def cleanup(self) -> None:
        pass
        
    def status(self) -> str:
        return self.state_machine.current_state.value
