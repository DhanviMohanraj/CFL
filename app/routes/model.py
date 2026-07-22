"""DriftAdapt Foundation Model Information Route.

Author: DriftAdapt Contributors
Purpose: Exposes GET /model endpoint returning foundation model metadata and memory specs.
Future Integration: Mounted in app/main.py.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, status, HTTPException

from app.services.lora.adapter_registry import AdapterRegistry
from app.services.lora.metadata_service import MetadataService
from app.services.lora.adapter_initializer import AdapterInitializer

from app.dependencies import (
    get_model_manager,
    get_lora_registry,
    get_lora_metadata_service,
    get_lora_initializer
)
from app.models.foundation import ModelManager
from app.schemas.lora_config import LoRAConfigurationRequest
from app.schemas.adapter_metadata import AdapterMetadataResponse
from app.schemas.initialization_result import InitializationResultResponse

router = APIRouter(tags=["Model", "LoRA"])


@router.get("/model", status_code=status.HTTP_200_OK)
def get_model_info(
    model_mgr: ModelManager = Depends(get_model_manager),
) -> Dict[str, Any]:
    """Returns foundation model metadata including architecture, tokenizer, quantization, precision, and memory footprint."""
    info = model_mgr.get_model_info()
    return info.to_dict()


@router.post("/model/lora/initialize", response_model=InitializationResultResponse, status_code=status.HTTP_200_OK)
def initialize_lora_adapter(
    request: LoRAConfigurationRequest,
    initializer: AdapterInitializer = Depends(get_lora_initializer)
) -> InitializationResultResponse:
    """Initializes a new LoRA adapter on the frozen foundation model."""
    try:
        result = initializer.initialize_adapter(request)
        if not result.success:
            # We return 400 for validation errors or failures, but with the detailed result payload.
            raise HTTPException(status_code=400, detail=result.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/lora/adapters", response_model=List[AdapterMetadataResponse])
def list_lora_adapters(
    registry: AdapterRegistry = Depends(get_lora_registry)
) -> List[AdapterMetadataResponse]:
    """Lists all registered LoRA adapters."""
    return registry.list_adapters()


@router.get("/model/lora/{adapter_id}", response_model=Dict[str, Any])
def get_lora_adapter_details(
    adapter_id: str,
    metadata_service: MetadataService = Depends(get_lora_metadata_service)
) -> Dict[str, Any]:
    """Returns detailed statistics and metadata for a specific adapter."""
    try:
        return metadata_service.get_adapter_statistics(adapter_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/model/lora/validate", response_model=Dict[str, Any])
def validate_lora_adapter(
    request: LoRAConfigurationRequest,
    initializer: AdapterInitializer = Depends(get_lora_initializer)
) -> Dict[str, Any]:
    """Validates configuration without full initialization. (Stub for future deeper pre-checks)."""
    # For now, we rely on the Pydantic schema validation provided by FastAPI.
    # Future logic could instantiate the ConfigBuilder and verify module existence without injection.
    return {"status": "PASSED_SCHEMA_VALIDATION", "adapter_name": request.adapter_name}

