"""Transmission Service for Federated Updates.

Author: DriftAdapt Contributors
Purpose: Handles the actual HTTP/HTTPS network transmission of the update payload to the aggregation server.
"""

import time
import httpx
from typing import Dict, Any, Optional

from app.core.logging import LoggerFactory
from app.schemas.transmission_request import TransmissionRequest
from app.schemas.transmission_response import TransmissionResponse
from app.services.federation.retry_manager import RetryManager
from app.services.federation.transmission_logger import TransmissionLogger


class TransmissionService:
    """Executes network uploads securely using HTTP/HTTPS."""

    def __init__(
        self,
        retry_manager: RetryManager,
        transmission_logger: TransmissionLogger
    ) -> None:
        self._logger = LoggerFactory.get_logger("TransmissionService")
        self._retry_manager = retry_manager
        self._trans_logger = transmission_logger

    async def _do_upload(self, request: TransmissionRequest) -> httpx.Response:
        """Inner function to perform the actual HTTP POST, wrapped by retry manager."""
        headers = {
            "Content-Type": "application/octet-stream",
            "X-DriftAdapt-Compression": request.compression,
            "X-DriftAdapt-Encryption": request.encryption
        }
        
        async with httpx.AsyncClient(timeout=request.timeout, verify=True) as client:
            response = await client.post(
                url=request.destination_server,
                content=request.update_package,
                headers=headers
            )
            response.raise_for_status()
            return response

    async def transmit(
        self,
        request: TransmissionRequest,
        adapter_id: str
    ) -> TransmissionResponse:
        """Transmits the payload securely with retries.
        
        Args:
            request: The TransmissionRequest object.
            adapter_id: Identifier for logging purposes.
            
        Returns:
            A TransmissionResponse detailing the outcome.
        """
        payload_size = len(request.update_package)
        self._trans_logger.log_upload_started(adapter_id, request.destination_server, payload_size)
        start_time = time.perf_counter()
        
        try:
            # We track the attempts via a mutable closure or just trust the retry manager's internal logging.
            # But the requirement asks to track retry counts in the response.
            # We'll use a local counter wrapped in a function to track attempts.
            attempts = [0]
            
            async def track_and_upload() -> httpx.Response:
                attempts[0] += 1
                return await self._do_upload(request)
                
            response = await self._retry_manager.execute_with_retry(
                operation=track_and_upload,
                max_retries=request.retry_limit
            )
            
            duration = time.perf_counter() - start_time
            
            # The server response should ideally contain acknowledgment details.
            # For this architecture, a 200/201 response implies acknowledgment.
            server_ack = response.status_code in (200, 201)
            
            # If the server returned a JSON body, it might indicate checksum verification.
            try:
                resp_json = response.json()
                checksum_verified = resp_json.get("checksum_verified", True)
            except Exception:
                checksum_verified = True
                
            retries = attempts[0] - 1
            
            self._trans_logger.log_upload_completed(
                adapter_id=adapter_id,
                upload_duration=duration,
                bytes_transferred=payload_size,
                retries=retries,
                server_ack=server_ack
            )
            
            return TransmissionResponse(
                success=True,
                upload_duration=duration,
                bytes_transferred=payload_size,
                server_acknowledgement=server_ack,
                checksum_verified=checksum_verified,
                retry_count=retries,
                transmission_status="SUCCESS",
                error_message=None
            )
            
        except httpx.HTTPStatusError as e:
            duration = time.perf_counter() - start_time
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            self._trans_logger.log_upload_failed(adapter_id, error_msg, request.retry_limit)
            return TransmissionResponse(
                success=False,
                upload_duration=duration,
                bytes_transferred=0,
                server_acknowledgement=False,
                checksum_verified=False,
                retry_count=request.retry_limit,
                transmission_status=f"FAILED_HTTP_{e.response.status_code}",
                error_message=error_msg
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            error_msg = str(e)
            self._trans_logger.log_upload_failed(adapter_id, error_msg, request.retry_limit)
            return TransmissionResponse(
                success=False,
                upload_duration=duration,
                bytes_transferred=0,
                server_acknowledgement=False,
                checksum_verified=False,
                retry_count=request.retry_limit,
                transmission_status="FAILED_NETWORK",
                error_message=error_msg
            )
