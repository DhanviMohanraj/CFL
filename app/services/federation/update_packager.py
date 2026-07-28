"""Update Packager Service for Federated Transmission.

Author: DriftAdapt Contributors
Purpose: Assembles, serializes, compresses, and encrypts the complete update package.
"""

import time
import io
import torch
from typing import Tuple, Optional

from app.core.logging import LoggerFactory
from app.schemas.client_update import ClientUpdate
from app.schemas.packaging_statistics import PackagingStatistics
from app.services.federation.compression_service import CompressionService
from app.services.federation.encryption_service import EncryptionService
from app.services.federation.checksum_service import ChecksumService


class UpdatePackager:
    """Service to assemble and serialize federated update payloads."""

    def __init__(
        self,
        compression_service: CompressionService,
        encryption_service: EncryptionService,
        checksum_service: ChecksumService
    ) -> None:
        self._logger = LoggerFactory.get_logger("UpdatePackager")
        self._compression_service = compression_service
        self._encryption_service = encryption_service
        self._checksum_service = checksum_service

    def package_update(
        self,
        client_update: ClientUpdate,
        compression_algo: str = "zstd",
        encryption_algo: str = "aes-256"
    ) -> Tuple[bytes, PackagingStatistics]:
        """Packages a ClientUpdate object for transmission.
        
        Process:
        1. Serializes the ClientUpdate (state dict + metadata) into bytes.
        2. Compresses the byte payload.
        3. Encrypts the compressed payload.
        
        Args:
            client_update: The populated ClientUpdate schema.
            compression_algo: Algorithm to use (e.g., 'zstd', 'gzip').
            encryption_algo: Algorithm to use (e.g., 'aes-256', 'none').
            
        Returns:
            Tuple containing:
            - The final, opaque byte payload ready for transmission.
            - Statistics describing the packaging process.
        """
        self._logger.info("Starting update packaging pipeline...")
        start_time = time.perf_counter()
        
        # 1. Serialization
        # Pydantic schemas with PyTorch tensors cannot easily be JSON-serialized.
        # We will use torch.save to serialize the entire object state via a memory buffer.
        buffer = io.BytesIO()
        try:
            # We dump the schema dict. Note: state_dict contains tensors.
            # torch.save safely handles dicts containing both standard types and tensors.
            torch.save(client_update.model_dump(), buffer)
        except Exception as e:
            self._logger.error("Failed to serialize the ClientUpdate.", error=str(e))
            raise RuntimeError(f"Serialization failed: {e}") from e
            
        raw_bytes = buffer.getvalue()
        original_size = len(raw_bytes)
        
        # 2. Compression
        if compression_algo != "none":
            compressed_bytes, comp_stats = self._compression_service.compress(raw_bytes, algorithm=compression_algo)
        else:
            compressed_bytes = raw_bytes
            comp_stats = {"compressed_size": original_size, "compression_ratio": 1.0}
            
        compressed_size = comp_stats["compressed_size"]
        
        # 3. Encryption
        encryption_time = 0.0
        if encryption_algo == "aes-256":
            encrypted_bytes, enc_stats = self._encryption_service.encrypt(compressed_bytes)
            encryption_time = enc_stats.get("duration_s", 0.0)
            final_payload = encrypted_bytes
        elif encryption_algo == "none":
            final_payload = compressed_bytes
        else:
            raise ValueError(f"Unsupported encryption algorithm: {encryption_algo}")
            
        total_duration = time.perf_counter() - start_time
        
        stats = PackagingStatistics(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=comp_stats["compression_ratio"],
            packaging_time=total_duration,
            encryption_time=encryption_time,
            upload_time=0.0  # Will be updated by TransmissionService
        )
        
        self._logger.info(
            f"Packaging complete. Final payload size: {len(final_payload)} bytes "
            f"(Original: {original_size}, Compression Ratio: {stats.compression_ratio:.2f}) "
            f"in {total_duration:.3f}s."
        )
        
        return final_payload, stats
