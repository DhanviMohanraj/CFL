"""DriftAdapt Client Dispatcher.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.federated.round_execution.execution_exceptions import ClientDispatchError


class ClientDispatcher:
    """Dispatches training tasks to clients."""
    
    def __init__(self) -> None:
        pass
        
    def dispatch(self, clients: List[str], month: int, config: Dict[str, Any]) -> None:
        """Mocks dispatching instructions to clients."""
        if not clients:
            raise ClientDispatchError("No clients provided for dispatch.")
            
        # Normally this would invoke the LocalTrainer or an RPC call to the Client Runtime
        for client in clients:
            pass
