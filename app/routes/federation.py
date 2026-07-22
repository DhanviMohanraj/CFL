"""Federation API Router.

Author: DriftAdapt Contributors
Purpose: Exposes endpoints for packaging, compressing, encrypting, and transmitting LoRA updates.
"""

import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.dependencies import (
    get_update_packager,
    get_checksum_service,
    get_compression_service,
    get_encryption_service,
    get_upload_queue
)
from app.schemas.client_update import ClientUpdate
from app.schemas.transmission_request import TransmissionRequest
from app.schemas.integrity_report import IntegrityReport
from app.services.federation.update_packager import UpdatePackager
from app.services.federation.checksum_service import ChecksumService
from app.services.federation.compression_service import CompressionService
from app.services.federation.encryption_service import EncryptionService
from app.services.federation.upload_queue import UploadQueue


router = APIRouter(prefix="/federation", tags=["Federation"])


# Basic request schemas for endpoints that don't take full models
class PackageRequest(BaseModel):
    adapter_id: str
    compression_algo: str = "zstd"
    encryption_algo: str = "aes-256"


class VerifyRequest(BaseModel):
    payload: bytes
    expected_checksum: str
    algorithm: str = "sha256"


class CompressRequest(BaseModel):
    payload: bytes
    algorithm: str = "zstd"


class EncryptRequest(BaseModel):
    payload: bytes


class UploadRequest(BaseModel):
    adapter_id: str
    destination_server: str
    priority: int = 1
    # For a real system, we'd pull the ClientUpdate from the DB or memory.
    # Here we accept it directly or assume it's pre-packaged.
    client_update: ClientUpdate


@router.post("/package", summary="Packages an update for transmission")
async def package_update(
    request: UploadRequest,
    packager: UpdatePackager = Depends(get_update_packager)
) -> Dict[str, Any]:
    """Serializes, compresses, and encrypts a client update."""
    try:
        final_payload, stats = packager.package_update(
            client_update=request.client_update,
            compression_algo="zstd",
            encryption_algo="aes-256"
        )
        return {
            "status": "SUCCESS",
            "payload_size": len(final_payload),
            "statistics": stats.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=IntegrityReport, summary="Verifies payload integrity")
async def verify_package(
    request: VerifyRequest,
    checksum_service: ChecksumService = Depends(get_checksum_service)
) -> IntegrityReport:
    """Verifies that the provided payload matches the expected checksum."""
    is_valid = checksum_service.verify_checksum(
        data=request.payload,
        expected_checksum=request.expected_checksum,
        algorithm=request.algorithm
    )
    
    return IntegrityReport(
        checksum=request.expected_checksum,
        hash_algorithm=request.algorithm,
        validation_status=is_valid,
        corruption_detected=not is_valid,
        verification_timestamp=0.0 # Will be populated by the schema default usually, or we can use time.time()
    )


@router.post("/compress", summary="Compresses a raw payload")
async def compress_package(
    request: CompressRequest,
    compression_service: CompressionService = Depends(get_compression_service)
) -> Dict[str, Any]:
    """Applies compression to a payload and returns statistics."""
    try:
        compressed, stats = compression_service.compress(request.payload, algorithm=request.algorithm)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/encrypt", summary="Encrypts a payload")
async def encrypt_package(
    request: EncryptRequest,
    encryption_service: EncryptionService = Depends(get_encryption_service)
) -> Dict[str, Any]:
    """Encrypts a payload using AES-256-GCM."""
    try:
        encrypted, stats = encryption_service.encrypt(request.payload)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", summary="Queues an update for transmission")
async def upload_update(
    request: UploadRequest,
    packager: UpdatePackager = Depends(get_update_packager),
    queue: UploadQueue = Depends(get_upload_queue)
) -> Dict[str, str]:
    """Packages the update and queues it for asynchronous transmission."""
    try:
        final_payload, _ = packager.package_update(
            client_update=request.client_update,
            compression_algo="zstd",
            encryption_algo="aes-256"
        )
        
        trans_req = TransmissionRequest(
            destination_server=request.destination_server,
            update_package=final_payload,
            priority=request.priority
        )
        
        job_id = str(uuid.uuid4())
        queue.enqueue_upload(job_id=job_id, adapter_id=request.adapter_id, request=trans_req)
        
        return {"status": "QUEUED", "job_id": job_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="Retrieves the upload queue status")
async def get_upload_status(
    queue: UploadQueue = Depends(get_upload_queue)
) -> Dict[str, Any]:
    """Returns the current state of the upload queue."""
    return queue.get_queue_statistics()


@router.get("/history", summary="Retrieves transmission history")
async def get_transmission_history() -> Dict[str, Any]:
    """Returns the history of completed and failed uploads (placeholder)."""
    # In a fully persistent system, this would query a database.
    # For now, it returns a placeholder structure.
    return {"history": []}
