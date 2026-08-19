"""DriftAdapt Federated Training Orchestrator.

Author: DriftAdapt Contributors
"""

from typing import List, Any

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
from app.training.local_trainer import LocalLoRATrainer
from app.training.flower_client import FlowerClient
from app.services.aggregation.flower_strategy import DriftAdaptStrategy
from app.services.aggregation.conflict_detector import ConflictDetector

import flwr as fl


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
            
    def run_month(self, available_clinics: List[str]) -> Any:
        """Runs a complete month of training using Flower Simulation and returns the history."""
        selected_clinics = self._clinic_scheduler.select_clinics(available_clinics)
        month = self._experiment_scheduler.current_month
        
        self._logger = self._metrics_bus # Assuming we have a logger, using metrics bus for event
        
        for clinic in selected_clinics:
            self._dataset_dispatcher.dispatch(clinic, month)
            
        # Define Flower Client Factory
        def client_fn(cid: str) -> fl.client.Client:
            clinic_id = selected_clinics[int(cid) % len(selected_clinics)]
            trainer = LocalLoRATrainer(
                trainer_id=f"trainer_{clinic_id}_{month}",
                clinic_id=clinic_id,
                month=month,
                config=self._config.to_dict() if hasattr(self._config, 'to_dict') else {},
                metrics_bus=self._metrics_bus
            )
            return FlowerClient(trainer).to_client()
            
        strategy = DriftAdaptStrategy(
            conflict_detector=ConflictDetector(),
            fraction_fit=1.0,
            fraction_evaluate=1.0,
            min_fit_clients=len(selected_clinics),
            min_evaluate_clients=len(selected_clinics),
            min_available_clients=len(selected_clinics)
        )
        
        self._metrics.publish_event(f"flower.simulation.starting", tags={"month": month, "rounds": self._config.communication_rounds})
        
        # Start Flower simulation for the month
        history = fl.simulation.start_simulation(
            client_fn=client_fn,
            num_clients=len(selected_clinics),
            config=fl.server.ServerConfig(num_rounds=self._config.communication_rounds),
            strategy=strategy,
            client_resources={"num_cpus": 1, "num_gpus": 1 if self._config.max_parallel_clients > 0 else 0}
        )
        
        self._metrics.publish_event("flower.simulation.completed", tags={"history_loss": str(history.losses_distributed)})
        
        if month % self._config.evaluation_interval == 0:
            self._evaluation_dispatcher.dispatch_monthly_evaluation(month)
            self._metrics.publish_event("evaluation.triggered")
            
        return history
            
    def run_round(self) -> None:
        """Deprecated: Replaced by Flower Server orchestration."""
        pass
        
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
