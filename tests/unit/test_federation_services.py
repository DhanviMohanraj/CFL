"""Unit Tests for Federation Services (Module 2.5).

Author: DriftAdapt Contributors
"""

import pytest
import torch
import asyncio
from typing import Dict, Any

from app.schemas.client_update import ClientUpdate
from app.services.federation.compression_service import CompressionService
from app.services.federation.encryption_service import EncryptionService
from app.services.federation.checksum_service import ChecksumService
from app.services.federation.bandwidth_optimizer import BandwidthOptimizer
from app.services.federation.metadata_builder import MetadataBuilder
from app.services.federation.retry_manager import RetryManager
from app.services.federation.update_extractor import UpdateExtractor


def test_compression_service_gzip():
    """Tests the gzip compression algorithm."""
    service = CompressionService()
    raw_data = b"hello " * 1000
    
    compressed, stats = service.compress(raw_data, algorithm="gzip")
    assert stats["algorithm"] == "gzip"
    assert stats["compression_ratio"] < 1.0
    assert len(compressed) < len(raw_data)
    
    decompressed = service.decompress(compressed, algorithm="gzip")
    assert decompressed == raw_data


def test_encryption_service_aes_gcm():
    """Tests AES-256-GCM encryption and decryption."""
    key = EncryptionService.generate_key()
    service = EncryptionService(symmetric_key=key)
    
    raw_data = b"sensitive federated update data"
    
    encrypted, stats = service.encrypt(raw_data)
    assert len(encrypted) > len(raw_data)
    assert stats["algorithm"] == "aes-256-gcm"
    
    decompressed = service.decrypt(encrypted)
    assert decompressed == raw_data


def test_encryption_service_tampering():
    """Tests that tampering with encrypted data raises an error."""
    key = EncryptionService.generate_key()
    service = EncryptionService(symmetric_key=key)
    
    raw_data = b"sensitive federated update data"
    encrypted, _ = service.encrypt(raw_data)
    
    # Tamper with the ciphertext (last byte)
    tampered = bytearray(encrypted)
    tampered[-1] ^= 0xFF
    
    with pytest.raises(ValueError, match="Decryption failed"):
        service.decrypt(bytes(tampered))


def test_checksum_service_sha256():
    """Tests SHA-256 checksum generation and verification."""
    service = ChecksumService()
    data = b"model weights"
    
    checksum, duration = service.generate_checksum(data, algorithm="sha256")
    assert len(checksum) == 64  # SHA-256 hex digest length
    
    assert service.verify_checksum(data, expected_checksum=checksum, algorithm="sha256")
    assert not service.verify_checksum(b"tampered", expected_checksum=checksum, algorithm="sha256")


def test_bandwidth_optimizer():
    """Tests the bandwidth optimizer recommendations."""
    service = BandwidthOptimizer()
    
    # High bandwidth -> zstd or none
    res1 = service.optimize(payload_size_bytes=1000000, estimated_bandwidth_mbps=100.0)
    assert res1["recommended_compression"] in ("none", "zstd")
    
    # Low bandwidth -> lzma or gzip
    res2 = service.optimize(payload_size_bytes=10000000, estimated_bandwidth_mbps=2.0, battery_level=0.1)
    assert res2["recommended_compression"] == "gzip"  # Saves battery


def test_metadata_builder():
    """Tests that metadata is populated correctly."""
    metadata = MetadataBuilder.build_metadata(
        project_name="DriftAdapt",
        foundation_model="qwen-3b",
        adapter_name="health-adapter",
        dataset_version="v1",
        training_duration=3600.5,
        personalization_round=2
    )
    
    assert metadata.project_name == "DriftAdapt"
    assert metadata.training_duration == 3600.5
    assert "pytorch" in metadata.framework_versions
    assert "os" in metadata.device_information


class DummyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.frozen_layer = torch.nn.Linear(10, 10)
        self.lora_layer = torch.nn.Linear(10, 10)
        
        # Freeze frozen_layer
        self.frozen_layer.weight.requires_grad = False
        self.frozen_layer.bias.requires_grad = False


def test_update_extractor():
    """Tests extraction of only trainable parameters."""
    model = DummyModel()
    extractor = UpdateExtractor()
    
    state_dict, count, size = extractor.extract_parameters(model)
    
    # Only lora_layer parameters should be extracted
    assert "lora_layer.weight" in state_dict
    assert "lora_layer.bias" in state_dict
    assert "frozen_layer.weight" not in state_dict
    
    expected_count = 10 * 10 + 10  # weight (100) + bias (10)
    assert count == expected_count


@pytest.mark.asyncio
async def test_retry_manager_success():
    """Tests retry manager with a successful operation."""
    manager = RetryManager()
    
    attempts = 0
    
    async def mock_operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Temporary failure")
        return "SUCCESS"
        
    # Will fail twice and succeed on the third attempt
    result = await manager.execute_with_retry(
        mock_operation,
        max_retries=3,
        initial_backoff_s=0.01,
        backoff_multiplier=1.0
    )
    
    assert result == "SUCCESS"
    assert attempts == 3


@pytest.mark.asyncio
async def test_retry_manager_exhausted():
    """Tests retry manager when retries are exhausted."""
    manager = RetryManager()
    
    async def always_fails():
        raise ValueError("Permanent failure")
        
    with pytest.raises(ValueError, match="Permanent failure"):
        await manager.execute_with_retry(
            always_fails,
            max_retries=2,
            initial_backoff_s=0.01
        )
