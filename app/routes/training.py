"""DriftAdapt Training API Routes.

Author: DriftAdapt Contributors
Purpose: Exposes endpoints to start, stop, and monitor local personalization training.
"""

from typing import Dict, Any, List

from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas.personalization_request import PersonalizationRequest
from app.schemas.personalization_response import PersonalizationResponse
from app.schemas.training_metrics import TrainingMetrics

from app.dependencies import (
    get_personalization_service,
    get_training_metrics_service,
    get_checkpoint_service
)
from app.services.training.personalization_service import PersonalizationService
from app.services.training.metrics_service import MetricsService
from app.services.training.checkpoint_service import CheckpointService

router = APIRouter(tags=["Training"])


@router.post("/training/start", response_model=PersonalizationResponse, status_code=status.HTTP_200_OK)
def start_personalization(
    request: PersonalizationRequest,
    personalization_service: PersonalizationService = Depends(get_personalization_service)
) -> PersonalizationResponse:
    """Initiates a local personalization fine-tuning run on the edge device."""
    try:
        response = personalization_service.start_personalization(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.model_dump())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/training/stop", status_code=status.HTTP_200_OK)
def stop_personalization(
    personalization_service: PersonalizationService = Depends(get_personalization_service)
) -> Dict[str, str]:
    """Gracefully terminates the active personalization run."""
    personalization_service.stop_personalization()
    return {"status": "Stop requested. Training will halt shortly."}


@router.post("/training/resume", response_model=PersonalizationResponse, status_code=status.HTTP_200_OK)
def resume_personalization(
    request: PersonalizationRequest,
    personalization_service: PersonalizationService = Depends(get_personalization_service)
) -> PersonalizationResponse:
    """Resumes training from a saved checkpoint."""
    if not request.resume_checkpoint:
        raise HTTPException(status_code=400, detail="resume_checkpoint path is required.")
    
    try:
        response = personalization_service.start_personalization(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.model_dump())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/status", response_model=Dict[str, Any])
def get_training_status(
    personalization_service: PersonalizationService = Depends(get_personalization_service)
) -> Dict[str, Any]:
    """Returns real-time execution telemetry for the active run."""
    return personalization_service.get_status()


@router.get("/training/metrics", response_model=List[TrainingMetrics])
def get_training_metrics(
    metrics_service: MetricsService = Depends(get_training_metrics_service)
) -> List[TrainingMetrics]:
    """Returns the historical epoch metrics of the current/last run."""
    return metrics_service.get_history()


@router.get("/training/checkpoints", response_model=List[str])
def list_training_checkpoints(
    checkpoint_service: CheckpointService = Depends(get_checkpoint_service)
) -> List[str]:
    """Lists available checkpoints. (Stub - requires path scanning implementation)."""
    # Placeholder for future scanning logic
    return []
