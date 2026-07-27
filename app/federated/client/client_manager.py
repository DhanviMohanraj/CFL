"""DriftAdapt Client Manager.

Author: DriftAdapt Contributors
"""

from typing import Dict, Optional

from app.core.logging.logger_factory import LoggerFactory
from app.federated.client.checkpoint_scheduler import CheckpointScheduler
from app.federated.client.client_registry import ClientRegistry
from app.federated.client.client_runtime import ClientRuntime
from app.federated.client.local_training_manager import LocalTrainingManager
from app.federated.client.training_history import TrainingHistory
from app.federated.client.training_orchestrator import TrainingOrchestrator


class ClientManager:
    """Manages multiple local client runtimes."""
    
    def __init__(self, registry: ClientRegistry) -> None:
        self._registry = registry
        self._runtimes: Dict[str, ClientRuntime] = {}
        self._logger = LoggerFactory.get_logger("ClientManager")
        
    def create_client(self, client_id: str, save_dir: str) -> ClientRuntime:
        """Constructs a full client stack."""
        history = TrainingHistory()
        training_mgr = LocalTrainingManager(history)
        ckpt_scheduler = CheckpointScheduler(save_dir)
        orchestrator = TrainingOrchestrator(training_mgr, ckpt_scheduler)
        
        runtime = ClientRuntime(client_id, orchestrator, self._registry)
        runtime.initialize()
        self._runtimes[client_id] = runtime
        return runtime
        
    def get_client(self, client_id: str) -> Optional[ClientRuntime]:
        return self._runtimes.get(client_id)
        
    def remove_client(self, client_id: str) -> None:
        runtime = self._runtimes.pop(client_id, None)
        if runtime:
            runtime.shutdown()
