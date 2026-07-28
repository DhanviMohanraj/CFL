"""Transmission Logger Service.

Author: DriftAdapt Contributors
Purpose: Specialized structured logger for transmission telemetry.
"""

from typing import Dict, Any, Optional

from app.core.logging import LoggerFactory


class TransmissionLogger:
    """Provides structured logging for the federation transmission lifecycle."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("TransmissionLogger")

    def log_upload_started(self, adapter_id: str, server_url: str, payload_size: int) -> None:
        """Logs the initiation of an upload."""
        self._logger.info(
            f"Upload started. Adapter: {adapter_id}, Target: {server_url}, Size: {payload_size} bytes."
        )

    def log_upload_completed(
        self,
        adapter_id: str,
        upload_duration: float,
        bytes_transferred: int,
        retries: int,
        server_ack: bool
    ) -> None:
        """Logs the successful completion of an upload."""
        speed_mbps = (bytes_transferred * 8 / (1024 * 1024)) / upload_duration if upload_duration > 0 else 0
        self._logger.info(
            f"Upload completed. Adapter: {adapter_id}, Duration: {upload_duration:.2f}s, "
            f"Transferred: {bytes_transferred} bytes, Speed: {speed_mbps:.2f} Mbps, "
            f"Retries: {retries}, Server Ack: {server_ack}."
        )

    def log_upload_failed(
        self,
        adapter_id: str,
        error_message: str,
        retries: int
    ) -> None:
        """Logs a failed upload attempt after all retries are exhausted."""
        self._logger.error(
            f"Upload FAILED permanently. Adapter: {adapter_id}, "
            f"Retries exhausted: {retries}. Reason: {error_message}"
        )
