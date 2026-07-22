"""Upload Queue Service for Federated Transmission.

Author: DriftAdapt Contributors
Purpose: Manages an asynchronous queue of transmission requests, allowing them to be processed in the background.
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from app.core.logging import LoggerFactory
from app.schemas.transmission_request import TransmissionRequest
from app.services.federation.transmission_service import TransmissionService


@dataclass
class QueuedUpload:
    """Represents an upload job in the queue."""
    job_id: str
    adapter_id: str
    request: TransmissionRequest
    status: str = "QUEUED"  # QUEUED, IN_PROGRESS, COMPLETED, FAILED
    error_message: Optional[str] = None


class UploadQueue:
    """Manages asynchronous uploads to the aggregation server."""

    def __init__(self, transmission_service: TransmissionService) -> None:
        self._logger = LoggerFactory.get_logger("UploadQueue")
        self._transmission_service = transmission_service
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._jobs: Dict[str, QueuedUpload] = {}
        self._worker_task: Optional[asyncio.Task] = None

    def start_worker(self) -> None:
        """Starts the background worker task if not already running."""
        if self._worker_task is None or self._worker_task.done():
            self._logger.info("Starting UploadQueue background worker.")
            self._worker_task = asyncio.create_task(self._process_queue())

    def stop_worker(self) -> None:
        """Stops the background worker task."""
        if self._worker_task and not self._worker_task.done():
            self._logger.info("Stopping UploadQueue background worker.")
            self._worker_task.cancel()

    async def _process_queue(self) -> None:
        """Continuously processes uploads from the priority queue."""
        try:
            while True:
                priority, job_id = await self._queue.get()
                job = self._jobs.get(job_id)
                
                if not job or job.status == "CANCELLED":
                    self._queue.task_done()
                    continue
                    
                job.status = "IN_PROGRESS"
                self._logger.info(f"Processing queued upload {job_id} for adapter {job.adapter_id}.")
                
                response = await self._transmission_service.transmit(job.request, job.adapter_id)
                
                if response.success:
                    job.status = "COMPLETED"
                else:
                    job.status = "FAILED"
                    job.error_message = response.error_message
                    
                self._queue.task_done()
                
        except asyncio.CancelledError:
            self._logger.info("UploadQueue worker task cancelled.")
        except Exception as e:
            self._logger.error("Unexpected error in UploadQueue worker.", error=str(e))

    def enqueue_upload(self, job_id: str, adapter_id: str, request: TransmissionRequest) -> str:
        """Adds a transmission request to the priority queue.
        
        Args:
            job_id: Unique identifier for this upload job.
            adapter_id: Identifier of the adapter being uploaded.
            request: The transmission request payload.
            
        Returns:
            The job_id.
        """
        job = QueuedUpload(
            job_id=job_id,
            adapter_id=adapter_id,
            request=request
        )
        self._jobs[job_id] = job
        
        # We use a tuple for the priority queue: (priority, job_id)
        # We must NOT await the queue.put if we want to call this synchronously from FastAPI routes,
        # so we will use put_nowait.
        try:
            self._queue.put_nowait((request.priority, job_id))
            self._logger.info(f"Enqueued upload job {job_id} with priority {request.priority}.")
            self.start_worker()
        except asyncio.QueueFull:
            self._logger.error(f"Failed to enqueue upload job {job_id}. Queue is full.")
            job.status = "FAILED"
            job.error_message = "Queue full"
            
        return job_id

    def get_status(self, job_id: str) -> Optional[QueuedUpload]:
        """Retrieves the status of a specific job."""
        return self._jobs.get(job_id)

    def cancel_upload(self, job_id: str) -> bool:
        """Cancels a queued upload if it hasn't started yet."""
        job = self._jobs.get(job_id)
        if job and job.status == "QUEUED":
            job.status = "CANCELLED"
            self._logger.info(f"Cancelled upload job {job_id}.")
            return True
        return False

    def get_queue_statistics(self) -> Dict[str, Any]:
        """Returns statistics about the current state of the queue."""
        queued = sum(1 for j in self._jobs.values() if j.status == "QUEUED")
        completed = sum(1 for j in self._jobs.values() if j.status == "COMPLETED")
        failed = sum(1 for j in self._jobs.values() if j.status == "FAILED")
        
        return {
            "total_jobs": len(self._jobs),
            "queued": queued,
            "completed": completed,
            "failed": failed,
            "queue_size": self._queue.qsize()
        }
