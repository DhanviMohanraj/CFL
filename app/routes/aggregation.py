"""Aggregation API Router.

Author: DriftAdapt Contributors
Purpose: Exposes federated aggregation orchestration endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.dependencies import get_aggregation_engine, get_aggregation_registry, get_aggregation_history
from app.schemas.aggregation_request import AggregationRequest
from app.schemas.aggregation_result import AggregationResult
from app.schemas.client_update_record import ClientUpdateRecord
from app.schemas.aggregation_statistics import AggregationStatistics
from app.services.aggregation.aggregation_engine import AggregationEngine
from app.services.aggregation.aggregation_registry import AggregationRegistry
from app.services.aggregation.aggregation_history import AggregationHistory


router = APIRouter(prefix="/aggregation", tags=["Aggregation"])


class RollbackRequest(BaseModel):
    target_version: str | None = None


@router.post("/submit", summary="Receives a packaged client update")
async def submit_client_update(
    client_id: str = Form(...),
    adapter_id: str = Form(...),
    local_epoch: int = Form(...),
    personalization_round: int = Form(...),
    dataset_size: int = Form(...),
    update_weight: float = Form(...),
    checksum: str = Form(...),
    upload_timestamp: float = Form(...),
    payload: UploadFile = File(...),
    engine: AggregationEngine = Depends(get_aggregation_engine)
) -> Dict[str, str]:
    """Receives an uploaded LoRA payload and stages it for aggregation."""
    try:
        record = ClientUpdateRecord(
            client_id=client_id,
            adapter_id=adapter_id,
            local_epoch=local_epoch,
            personalization_round=personalization_round,
            dataset_size=dataset_size,
            update_weight=update_weight,
            checksum=checksum,
            upload_timestamp=upload_timestamp
        )
        
        payload_bytes = await payload.read()
        engine.submit_client_update(record, payload_bytes)
        return {"status": "STAGED", "client_id": client_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", response_model=AggregationResult, summary="Triggers an aggregation round")
async def run_aggregation(
    request: AggregationRequest,
    engine: AggregationEngine = Depends(get_aggregation_engine)
) -> AggregationResult:
    """Orchestrates validation, filtering, merging, and versioning of staged client updates."""
    try:
        return engine.run_aggregation(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/global", summary="Retrieves the latest global adapter metadata")
async def get_latest_global_adapter(
    registry: AggregationRegistry = Depends(get_aggregation_registry)
) -> Dict[str, Any]:
    """Returns the metadata of the currently active global adapter."""
    adapter = registry.get_current_global_adapter()
    if not adapter:
        raise HTTPException(status_code=404, detail="No global adapter found.")
        
    # Model dump but exclude the large state dict
    return adapter.model_dump(exclude={"state_dict"})


@router.get("/history", summary="Retrieves the aggregation history ledger")
async def get_aggregation_history(
    history: AggregationHistory = Depends(get_aggregation_history)
) -> List[AggregationResult]:
    """Returns all historical aggregation rounds."""
    return history.get_history()


@router.get("/statistics", summary="Retrieves global aggregation statistics")
async def get_aggregation_statistics(
    history: AggregationHistory = Depends(get_aggregation_history)
) -> Dict[str, Any]:
    """Calculates overall lifetime statistics for the federated node."""
    rounds = history.get_history()
    successful = [r for r in rounds if r.success]
    
    return {
        "total_rounds_attempted": len(rounds),
        "total_rounds_successful": len(successful),
        "total_clients_aggregated": sum(len(r.aggregated_clients) for r in successful),
        "total_bandwidth_mb": sum(r.aggregation_statistics.communication_cost for r in successful)
    }


@router.get("/clients", summary="Retrieves all registered clients")
async def get_registered_clients(
    registry: AggregationRegistry = Depends(get_aggregation_registry)
) -> List[str]:
    """Returns a list of all client IDs that have participated in the past."""
    return registry.get_registered_clients()


@router.post("/rollback", summary="Rolls back the global adapter version")
async def rollback_version(
    request: RollbackRequest,
    engine: AggregationEngine = Depends(get_aggregation_engine)
) -> Dict[str, Any]:
    """Rolls back the active adapter to a previous known version."""
    success = engine.rollback(request.target_version)
    if success:
        return {"status": "SUCCESS", "message": "Rollback completed."}
    raise HTTPException(status_code=400, detail="Rollback failed.")
