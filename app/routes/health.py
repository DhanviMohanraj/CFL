"""DriftAdapt Health Route.

Author: DriftAdapt Contributors
Purpose: Exposes GET /health endpoint for application health and subsystem statuses.
Future Integration: Mounted in app/main.py.
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, status

from app.container import ServiceContainer
from app.dependencies import get_container

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def get_health(container: ServiceContainer = Depends(get_container)) -> Dict[str, Any]:
    """Returns application health, uptime, version, timestamp, and subsystem statuses."""
    config = container.config_manager().get_config()

    return {
        "status": "HEALTHY",
        "project_name": config.system.project_name,
        "project_version": config.system.project_version,
        "timestamp": time.time(),
        "uptime_seconds": container.get_uptime_seconds(),
        "is_ready": container.is_ready,
        "services": container.get_services_status(),
    }
