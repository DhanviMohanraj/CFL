"""DriftAdapt Experiment Manager.

Author: DriftAdapt Contributors
"""

import uuid
import time
from typing import Optional

from app.training.experiment_schema import ExperimentMetadata
from app.training.experiment_registry import ExperimentRegistry
from app.training.experiment_history import ExperimentHistory
from app.training.experiment_logger import ExperimentLogger
from app.training.training_configuration import TrainingConfiguration
from app.training.experiment_exceptions import ExperimentInitializationError


class ExperimentManager:
    """Manages creation, termination, and metadata for experiments."""
    
    def __init__(self, registry: ExperimentRegistry) -> None:
        self._registry = registry
        self._history = ExperimentHistory()
        self._logger: Optional[ExperimentLogger] = None
        self._current_experiment: Optional[ExperimentMetadata] = None
        
    def create(self, config: TrainingConfiguration) -> str:
        """Creates a new experiment."""
        exp_id = str(uuid.uuid4())
        self._logger = ExperimentLogger(exp_id)
        
        self._current_experiment = ExperimentMetadata(
            experiment_id=exp_id,
            name=config.experiment_name,
            start_time=time.time(),
            config=config.model_dump()
        )
        
        self._registry.register(self._current_experiment)
        self._history.record_event("EXPERIMENT_CREATED", {"experiment_id": exp_id})
        self._logger.info(f"Experiment {exp_id} created.")
        
        return exp_id
        
    def start(self, experiment_id: str) -> None:
        if not self._current_experiment or self._current_experiment.experiment_id != experiment_id:
            raise ExperimentInitializationError("Experiment not found or mismatch.")
        self._current_experiment.status = "STARTED"
        self._history.record_event("EXPERIMENT_STARTED", {"experiment_id": experiment_id})
        self._logger.info(f"Experiment {experiment_id} started.")
        
    def pause(self, experiment_id: str) -> None:
        if self._current_experiment and self._current_experiment.experiment_id == experiment_id:
            self._current_experiment.status = "PAUSED"
            self._history.record_event("EXPERIMENT_PAUSED", {"experiment_id": experiment_id})
            self._logger.info(f"Experiment {experiment_id} paused.")
            
    def resume(self, experiment_id: str) -> None:
        if self._current_experiment and self._current_experiment.experiment_id == experiment_id:
            self._current_experiment.status = "STARTED"
            self._history.record_event("EXPERIMENT_RESUMED", {"experiment_id": experiment_id})
            self._logger.info(f"Experiment {experiment_id} resumed.")
            
    def terminate(self, experiment_id: str, success: bool = False) -> None:
        if self._current_experiment and self._current_experiment.experiment_id == experiment_id:
            self._current_experiment.status = "COMPLETED" if success else "FAILED"
            self._current_experiment.end_time = time.time()
            self._history.record_event("EXPERIMENT_TERMINATED", {"experiment_id": experiment_id, "success": success})
            self._logger.info(f"Experiment {experiment_id} terminated (Success: {success}).")
            
    def archive(self, experiment_id: str) -> None:
        self._registry.archive(experiment_id)
        if self._logger:
            self._logger.info(f"Experiment {experiment_id} archived.")
            
    def status(self) -> str:
        return self._current_experiment.status if self._current_experiment else "NONE"
        
    def summary(self) -> dict:
        if not self._current_experiment:
            return {}
        return self._current_experiment.model_dump()
