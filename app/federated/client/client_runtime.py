"""DriftAdapt Client Runtime.

Author: DriftAdapt Contributors
"""

from typing import Dict, Optional

from app.core.config.config_manager import ConfigManager
from app.core.logging.logger_factory import LoggerFactory
from app.federated.client.client_exceptions import RuntimeStateError
from app.federated.client.client_registry import ClientRegistry
from app.federated.client.client_schema import ClientIdentity
from app.federated.client.client_session import ClientSession
from app.federated.client.runtime_state import RuntimeState
from app.federated.client.training_orchestrator import TrainingOrchestrator


class ClientRuntime:
    """Manages the full lifecycle of a local federated client."""
    
    def __init__(self, 
                 client_id: str, 
                 orchestrator: TrainingOrchestrator, 
                 registry: ClientRegistry,
                 configs_dir: Optional[str] = None) -> None:
        self.client_id = client_id
        self._orchestrator = orchestrator
        self._registry = registry
        self._logger = LoggerFactory.get_logger(f"ClientRuntime-{client_id}")
        
        config = ConfigManager(configs_dir).get_config()
        self._client_config = getattr(config, "client", None)
        
        self._identity = ClientIdentity(client_id=client_id)
        self._session: Optional[ClientSession] = None
        
    def initialize(self) -> None:
        """Registers client and prepares runtime."""
        self._registry.register(self._identity)
        self._logger.info("Client runtime initialized.")
        
    def start(self, round_num: int = 1) -> None:
        """Starts a new federated round."""
        if self._session and self._session.current_state not in (RuntimeState.COMPLETED, RuntimeState.FAILED, RuntimeState.STOPPED):
            raise RuntimeStateError("Cannot start a new session while one is active.")
            
        self._session = ClientSession(self.client_id, round_num)
        self._session.transition_to(RuntimeState.PREPARING)
        self._orchestrator.prepare_training()
        
        self._session.transition_to(RuntimeState.TRAINING)
        try:
            self._orchestrator.begin_training()
            self._session.transition_to(RuntimeState.PACKAGING)
            # Would normally hand off to communication manager here
            self._orchestrator.finish_training()
            self._session.transition_to(RuntimeState.COMPLETED)
        except Exception as e:
            self._logger.error(f"Round failed: {e}")
            self._session.increment_failure()
            
    def pause(self) -> None:
        """Pauses the current session."""
        if not self._session or self._session.current_state != RuntimeState.TRAINING:
            raise RuntimeStateError("Can only pause during active training.")
        self._orchestrator.abort_training()
        self._session.transition_to(RuntimeState.STOPPED)
        
    def resume(self) -> None:
        """Resumes a stopped session."""
        if not self._session or self._session.current_state != RuntimeState.STOPPED:
            raise RuntimeStateError("Can only resume a stopped session.")
        self._session.transition_to(RuntimeState.TRAINING)
        self._orchestrator.prepare_training() # Reset abort flag
        try:
            self._orchestrator.begin_training()
            self._session.transition_to(RuntimeState.COMPLETED)
        except Exception as e:
            self._session.increment_failure()
            
    def shutdown(self) -> None:
        """Shuts down the client runtime."""
        if self._session and self._session.current_state == RuntimeState.TRAINING:
            self.pause()
        self._registry.unregister(self.client_id)
        self._logger.info("Client runtime shut down.")
        
    def status(self) -> str:
        """Returns current state."""
        return self._session.current_state.value if self._session else RuntimeState.IDLE.value
        
    def heartbeat(self) -> None:
        """Sends a heartbeat to the registry."""
        self._registry.heartbeat(self.client_id)
