"""Inference API Router.

Author: DriftAdapt Contributors
Purpose: Exposes personalized LLM generation REST endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.dependencies import get_inference_engine, get_adapter_loader, get_adapter_registry, get_inference_history, get_inference_metrics
from app.schemas.inference_request import InferenceRequest
from app.schemas.inference_response import InferenceResponse
from app.schemas.inference_history import InferenceHistory
from app.schemas.adapter_selection import AdapterSelection
from app.services.inference.inference_engine import InferenceEngine
from app.services.inference.adapter_loader import AdapterLoader
from app.services.inference.adapter_registry import AdapterRegistry
from app.services.inference.inference_history_manager import InferenceHistoryManager
from app.services.inference.inference_metrics import InferenceMetrics


router = APIRouter(prefix="/inference", tags=["Inference"])


class LoadAdapterRequest(BaseModel):
    adapter_id: str
    adapter_path: str
    version: str = "latest"


@router.post("/generate", response_model=InferenceResponse, summary="Generates a standard text response")
async def generate_text(
    request: InferenceRequest,
    engine: InferenceEngine = Depends(get_inference_engine)
) -> InferenceResponse:
    """Executes a standard end-to-end forward generation pass on the foundation model."""
    try:
        return engine.run_generation(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream", summary="Streams generated text via Server-Sent Events (SSE)")
async def generate_stream(
    request: InferenceRequest,
    engine: InferenceEngine = Depends(get_inference_engine)
) -> StreamingResponse:
    """Executes generation yielding tokens iteratively to lower Time-To-First-Token latency."""
    try:
        request.stream = True
        return StreamingResponse(
            engine.run_streaming(request),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="Retrieves the inference ledger")
async def get_history(
    limit: int = 100,
    history_manager: InferenceHistoryManager = Depends(get_inference_history)
) -> List[InferenceHistory]:
    """Returns recent requests and their token footprint analytics."""
    return history_manager.get_history(limit)


@router.get("/statistics", summary="Retrieves inference engine telemetry")
async def get_statistics(
    registry: AdapterRegistry = Depends(get_adapter_registry),
    metrics: InferenceMetrics = Depends(get_inference_metrics)
) -> Dict[str, Any]:
    """Returns global metrics including cache hit rates and avg latencies."""
    active_count = len(registry.get_loaded_adapters())
    return metrics.get_statistics(active_count).model_dump()


@router.get("/adapters", summary="Retrieves loaded LoRA adapters")
async def get_adapters(
    registry: AdapterRegistry = Depends(get_adapter_registry)
) -> List[AdapterSelection]:
    """Lists all PEFT adapters currently held in model memory."""
    return registry.get_loaded_adapters()


@router.post("/load", summary="Loads an adapter from disk")
async def load_adapter(
    request: LoadAdapterRequest,
    loader: AdapterLoader = Depends(get_adapter_loader)
) -> Dict[str, str]:
    """Ingests a LoRA checkpoint into the foundation model VRAM."""
    success = loader.load_adapter(request.adapter_id, request.adapter_path, request.version)
    if success:
        return {"status": "SUCCESS", "message": f"Adapter {request.adapter_id} loaded."}
    raise HTTPException(status_code=400, detail="Failed to load adapter.")


@router.post("/unload/{adapter_id}", summary="Unloads an adapter to free VRAM")
async def unload_adapter(
    adapter_id: str,
    loader: AdapterLoader = Depends(get_adapter_loader)
) -> Dict[str, str]:
    """Unmounts an adapter from memory."""
    success = loader.unload_adapter(adapter_id)
    if success:
        return {"status": "SUCCESS", "message": f"Adapter {adapter_id} unloaded."}
    raise HTTPException(status_code=400, detail="Failed to unload adapter.")
