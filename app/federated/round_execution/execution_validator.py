"""DriftAdapt Execution Validator.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.federated.round_execution.execution_exceptions import RoundInitializationError


class ExecutionValidator:
    """Validates configuration and readiness before starting a round."""
    
    def validate_round_config(self, config: Dict[str, Any]) -> None:
        if config.get("max_parallel_clients", 0) <= 0:
            raise RoundInitializationError("max_parallel_clients must be > 0")
        if config.get("client_timeout", 0) <= 0:
            raise RoundInitializationError("client_timeout must be > 0")
            
    def validate_clients(self, clients: List[str]) -> None:
        if not clients:
            raise RoundInitializationError("No clients selected for the round.")
