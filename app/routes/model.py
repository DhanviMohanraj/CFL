"""DriftAdapt Foundation Model Information Route.

Author: DriftAdapt Contributors
Purpose: Exposes GET /model endpoint returning foundation model metadata and memory specs.
Future Integration: Mounted in app/main.py.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from app.dependencies import get_model_manager
from app.models.foundation import ModelManager

router = APIRouter(tags=["Model"])


@router.get("/model", status_code=status.HTTP_200_OK)
def get_model_info(
    model_mgr: ModelManager = Depends(get_model_manager),
) -> Dict[str, Any]:
    """Returns foundation model metadata including architecture, tokenizer, quantization, precision, and memory footprint."""
    info = model_mgr.get_model_info()
    return info.to_dict()
