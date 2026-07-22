"""Checksum Service for Federated Updates.

Author: DriftAdapt Contributors
Purpose: Computes cryptographic hashes for payload integrity verification.
"""

import hashlib
import time
from typing import Tuple

from app.core.logging import LoggerFactory


class ChecksumService:
    """Generates and verifies cryptographic checksums for data integrity."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("ChecksumService")

    def generate_checksum(self, data: bytes, algorithm: str = "sha256") -> Tuple[str, float]:
        """Computes the checksum for the given byte data.
        
        Args:
            data: Raw bytes to hash.
            algorithm: 'sha256' or 'sha512'.
            
        Returns:
            Tuple containing:
            - The hex digest string of the checksum.
            - Duration taken to compute the hash in seconds.
            
        Raises:
            ValueError: If the algorithm is unsupported.
        """
        start_time = time.perf_counter()
        
        if algorithm.lower() == "sha256":
            hasher = hashlib.sha256()
        elif algorithm.lower() == "sha512":
            hasher = hashlib.sha512()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
        hasher.update(data)
        checksum = hasher.hexdigest()
        
        duration = time.perf_counter() - start_time
        self._logger.debug(f"Computed {algorithm} checksum in {duration:.3f}s.")
        
        return checksum, duration

    def verify_checksum(self, data: bytes, expected_checksum: str, algorithm: str = "sha256") -> bool:
        """Verifies if the data matches the expected checksum.
        
        Args:
            data: Raw bytes to hash.
            expected_checksum: The expected hex digest string.
            algorithm: 'sha256' or 'sha512'.
            
        Returns:
            True if the checksum matches, False otherwise.
        """
        actual_checksum, _ = self.generate_checksum(data, algorithm)
        is_valid = actual_checksum == expected_checksum
        
        if not is_valid:
            self._logger.warning(
                f"Checksum mismatch! Expected {expected_checksum}, but got {actual_checksum}."
            )
            
        return is_valid
