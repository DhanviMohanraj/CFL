"""DriftAdapt Federated Training Orchestrator.

Author: DriftAdapt Contributors
"""

from typing import List

from app.core.metrics.metrics_bus import MetricsBus
from app.training.training_configuration import TrainingConfiguration
from app.training.experiment_state import ExperimentState
from app.training.state_machine import StateMachine
from app.training.lifecycle_manager import LifecycleManager
from app.training.experiment_manager import ExperimentManager
from app.training.experiment_registry import ExperimentRegistry
from app.training.experiment_scheduler import ExperimentScheduler
from app.training.round_scheduler import RoundScheduler
from app.training.clinic_scheduler import ClinicScheduler, AllClinicsStrategy
from app.training.dataset_dispatcher import DatasetDispatcher
from app.training.aggregation_dispatcher import AggregationDispatcher
from app.training.evaluation_dispatcher import EvaluationDispatcher
from app.training.progress_tracker import ProgressTracker
from app.training.experiment_validator import ExperimentValidator
from app.training.experiment_metrics import ExperimentMetrics
from app.training.checkpoint_orchestrator import CheckpointOrchestrator
from app.training.resource_allocator import ResourceAllocator
from app.training.experiment_exceptions import ExperimentError


class FederatedTrainingOrchestrator:
    """The central controller for federated learning experiments."""
    
    def __init__(self, config: TrainingConfiguration) -> None:
        self._config = config
        
        self._metrics_bus = MetricsBus()
        self._metrics = ExperimentMetrics(self._metrics_bus)
        
        self._registry = ExperimentRegistry()
        self._manager = ExperimentManager(self._registry)
        
        self._state_machine = StateMachine()
        self._lifecycle = LifecycleManager(self._state_machine)
        self._validator = ExperimentValidator()
        
        self._clinic_scheduler = ClinicScheduler(AllClinicsStrategy())
        self._experiment_scheduler = ExperimentScheduler(config.total_months)
        self._round_scheduler = RoundScheduler(config.communication_rounds)
        
        self._dataset_dispatcher = DatasetDispatcher()
        self._aggregation_dispatcher = AggregationDispatcher()
        self._evaluation_dispatcher = EvaluationDispatcher()
        
        self._progress = ProgressTracker(config.communication_rounds, config.total_months)
        self._checkpoints = CheckpointOrchestrator()
        self._resources = ResourceAllocator(config.max_parallel_clients)
        
        self._experiment_id = None
        
    def initialize(self) -> None:
        """Initializes the orchestrator and all its components."""
        self._validator.validate_configuration(self._config)
        self._experiment_id = self._manager.create(self._config)
        self._lifecycle.start()
        
    def run_experiment(self, available_clinics: List[str]) -> None:
        """Runs the full experiment."""
        self._validator.validate_clinics(available_clinics)
        self._manager.start(self._experiment_id)
        self._metrics.publish_event("experiment.started")
        
        try:
            while not self._experiment_scheduler.is_complete():
                self.run_month(available_clinics)
                self._experiment_scheduler.next_month()
                self._progress.record_month_completion()
                self._metrics.publish_event("training.month.completed")
                
            self._lifecycle.complete()
            self._manager.terminate(self._experiment_id, success=True)
            self._metrics.publish_event("experiment.completed")
            
        except Exception as e:
            self._lifecycle.fail()
            self._manager.terminate(self._experiment_id, success=False)
            self._metrics.publish_event("experiment.failed", tags={"reason": str(e)})
            raise ExperimentError(f"Experiment failed: {e}") from e
            
    def run_month(self, available_clinics: List[str]) -> None:
        """Runs a complete month of training."""
        selected_clinics = self._clinic_scheduler.select_clinics(available_clinics)
        month = self._experiment_scheduler.current_month
        
        for clinic in selected_clinics:
            self._dataset_dispatcher.dispatch(clinic, month)
            
        # Reset round scheduler for the month
        self._round_scheduler = RoundScheduler(self._config.communication_rounds)
        
        while not self._round_scheduler.is_complete():
            self.run_round()
            self._round_scheduler.next_round()
            self._progress.record_round_completion()
            self._metrics.publish_event("training.round.completed")
            
            if self._config.aggregation_after_each_round:
                self._aggregation_dispatcher.dispatch_aggregation(f"month_{month}_round_{self._round_scheduler.current_round}")
                self._metrics.publish_event("aggregation.triggered")
                
        if month % self._config.evaluation_interval == 0:
            self._evaluation_dispatcher.dispatch_monthly_evaluation(month)
            self._metrics.publish_event("evaluation.triggered")
            
    def run_round(self) -> None:
        """Mocks the execution of a single federated communication round."""
        self._state_machine.transition_to(ExperimentState.TRAINING)
        self._state_machine.transition_to(ExperimentState.COMMUNICATING)
        self._state_machine.transition_to(ExperimentState.AGGREGATING)
        self._state_machine.transition_to(ExperimentState.PREPARING)
        
    def pause(self) -> None:
        self._lifecycle.pause()
        if self._experiment_id:
            self._manager.pause(self._experiment_id)
            
    def resume(self) -> None:
        self._lifecycle.resume()
        if self._experiment_id:
            self._manager.resume(self._experiment_id)
            
    def stop(self) -> None:
        self._lifecycle.cancel()
        if self._experiment_id:
            self._manager.terminate(self._experiment_id, success=False)
            
    def shutdown(self) -> None:
        if self._experiment_id:
            self._manager.archive(self._experiment_id)
