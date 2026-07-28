"""Tests for Adapter Checksum Engine.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.checksum import ChecksumEngine
from app.adapters.exceptions import ChecksumMismatch


def test_compute_checksum():
    """Test stable checksum computation."""
    engine = ChecksumEngine()
    data = b"test federated payload"
    checksum = engine.compute_checksum(data)
    
    assert isinstance(checksum, str)
    assert len(checksum) == 64  # SHA256 length
    
    # Check deterministic behavior
    assert checksum == engine.compute_checksum(data)


def test_verify_checksum():
    """Test checksum integrity verification."""
    engine = ChecksumEngine()
    data = b"test federated payload"
    checksum = engine.compute_checksum(data)
    
    # Should pass silently
    engine.verify_checksum(data, checksum)
    
    # Should fail on corruption
    with pytest.raises(ChecksumMismatch):
        engine.verify_checksum(b"tampered federated payload", checksum)
