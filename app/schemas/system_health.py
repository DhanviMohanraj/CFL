"""System Health Schema.

Author: DriftAdapt Contributors
Purpose: Represents the overall real-time operational status of the host machine and AI services.
"""

import time
from typing import Optional
from pydantic import BaseModel, Field


class SystemHealth(BaseModel):
    """Snapshot of system health and hardware availability."""
    
    overall_status: str = Field(default="HEALTHY", description="Aggregate status (e.g., HEALTHY, DEGRADED, OFFLINE)")
    
    model_loaded: bool = Field(default=False, description="Is the foundation model currently in memory?")
    adapter_loaded: bool = Field(default=False, description="Is at least one adapter loaded?")
    active_adapter: Optional[str] = Field(default=None, description="The ID of the currently active adapter, if any")
    
    memory_status: str = Field(default="OK", description="RAM availability status")
    gpu_status: str = Field(default="NOT_AVAILABLE", description="VRAM availability status")
    storage_status: str = Field(default="OK", description="Disk space availability status")
    api_status: str = Field(default="ONLINE", description="FastAPI service status")
    
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of the health check")
