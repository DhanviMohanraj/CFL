"""DriftAdapt System Information Route.

Author: DriftAdapt Contributors
Purpose: Exposes GET /system endpoint returning hardware, OS, CPU, GPU, RAM, VRAM, and execution device specs.
Future Integration: Mounted in app/main.py.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from app.core.runtime import RuntimeManager
from app.dependencies import get_runtime_manager

router = APIRouter(tags=["System"])


@router.get("/system", status_code=status.HTTP_200_OK)
def get_system(
    runtime_mgr: RuntimeManager = Depends(get_runtime_manager),
) -> Dict[str, Any]:
    """Returns runtime environment information including OS, Python version, CPU, GPU, CUDA, RAM, and execution device."""
    info = runtime_mgr.get_runtime_info()
    return info.model_dump()
