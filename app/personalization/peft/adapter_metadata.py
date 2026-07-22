"""DriftAdapt PEFT Adapter Metadata.

Author: DriftAdapt Contributors
Purpose: Dataclass defining the state and metadata of an injected adapter.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class AdapterMetadata:
    """Metadata detailing the injected PEFT adapter state."""
    
    adapter_name: str
    rank: int
    alpha: float
    target_modules: List[str]
    trainable_parameters: int = 0
    total_parameters: int = 0
    injection_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @property
    def trainable_ratio(self) -> float:
        """Returns the ratio of trainable parameters to total parameters."""
        if self.total_parameters == 0:
            return 0.0
        return self.trainable_parameters / self.total_parameters
