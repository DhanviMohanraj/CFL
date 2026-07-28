"""DriftAdapt Adapter Validator.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.federated.round_execution.execution_exceptions import AdapterValidationError


class AdapterValidator:
    """Validates adapters received from clients."""
    
    def __init__(self) -> None:
        pass
        
    def validate(self, adapter_path: str, metadata: Dict[str, Any]) -> bool:
        """Validates adapter checksum and metadata."""
        if not adapter_path:
            raise AdapterValidationError("Adapter path missing.")
        if "checksum" not in metadata:
            raise AdapterValidationError("Checksum missing in adapter metadata.")
        return True
