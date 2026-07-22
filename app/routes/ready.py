"""DriftAdapt Readiness Route.

Author: DriftAdapt Contributors
Purpose: Exposes GET /ready endpoint responding with 200 OK when ready or 503 Service Unavailable when unready.
Future Integration: Mounted in app/main.py.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, Response, status

from app.container import ServiceContainer
from app.dependencies import get_container

router = APIRouter(tags=["Readiness"])


@router.get("/ready")
def get_ready(
    response: Response,
    container: ServiceContainer = Depends(get_container),
) -> Dict[str, Any]:
    """Returns application readiness status. Responds with HTTP 503 if startup sequence has not completed."""
    if not container.is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "NOT_READY",
            "message": "Application initialization sequence in progress or unready.",
            "uptime_seconds": container.get_uptime_seconds(),
        }

    response.status_code = status.HTTP_200_OK
    return {
        "status": "READY",
        "message": "Application is ready to serve traffic.",
        "uptime_seconds": container.get_uptime_seconds(),
    }
