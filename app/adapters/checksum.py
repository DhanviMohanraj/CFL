"""DriftAdapt Adapter Checksum Engine.

Author: DriftAdapt Contributors
Purpose: Computes and verifies SHA256 checksums of serialized adapter state.
"""

import hashlib
import time
from typing import Optional

from app.adapters.exceptions import ChecksumMismatch
from app.adapters.metrics import AdapterMetricsPublisher
from app.core.logging.logger_factory import LoggerFactory


class ChecksumEngine:
    """Provides hashing and integrity verification for serialized adapters."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("ChecksumEngine")
        self._metrics = AdapterMetricsPublisher()

    def compute_checksum(self, data: bytes) -> str:
        """Computes a SHA256 checksum for the provided byte payload.
        
        Args:
            data: The serialized adapter payload as bytes.
            
        Returns:
            The hex digest string of the checksum.
        """
        start_time = time.perf_counter()
        
        hasher = hashlib.sha256()
        hasher.update(data)
        checksum = hasher.hexdigest()
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        self._metrics.publish("checksum_time", duration_ms)
        self._logger.debug(f"Computed checksum {checksum[:8]}... in {duration_ms:.2f}ms")
        
        return checksum

    def compare_checksum(self, expected: str, actual: str) -> bool:
        """Compares two checksum strings securely."""
        # Using string equality is fine here, or hmac.compare_digest for timing attack resistance
        # Given this is just integrity (not secrets), standard == is acceptable
        return expected == actual

    def verify_checksum(self, data: bytes, expected_checksum: str) -> None:
        """Verifies the integrity of the data against the expected checksum.
        
        Args:
            data: The serialized adapter payload as bytes.
            expected_checksum: The expected SHA256 hex digest.
            
        Raises:
            ChecksumMismatch: If the computed checksum does not match expected.
        """
        actual_checksum = self.compute_checksum(data)
        if not self.compare_checksum(expected_checksum, actual_checksum):
            self._logger.error(
                f"Checksum mismatch! Expected: {expected_checksum}, Actual: {actual_checksum}"
            )
            raise ChecksumMismatch(f"Expected {expected_checksum}, but got {actual_checksum}")
        
        self._logger.debug(f"Checksum {expected_checksum[:8]}... verified successfully.")
