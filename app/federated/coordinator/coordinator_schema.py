"""DriftAdapt Coordinator Schema.

Author: DriftAdapt Contributors
"""

import time
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class FederatedRoundMetadata(BaseModel):
    """Metadata regarding a single federated communication round."""
    round_id: str = Field(..., description="Unique ID for the round.")
    global_round: int = Field(..., description="Global round number.")
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    status: str = Field(default="INITIALIZED", description="Current status of the round.")
    selected_clients: List[str] = Field(default_factory=list, description="Clients selected for this round.")
    completed_clients: List[str] = Field(default_factory=list, description="Clients that successfully uploaded.")
    failed_clients: List[str] = Field(default_factory=list, description="Clients that failed or timed out.")


class CoordinatorStatistics(BaseModel):
    """Aggregated statistics for the coordinator."""
    total_rounds: int = 0
    successful_rounds: int = 0
    failed_rounds: int = 0
    total_client_participations: int = 0
    total_client_failures: int = 0
