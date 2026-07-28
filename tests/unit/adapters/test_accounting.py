"""Tests for Communication Accounting.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.communication_accounting import CommunicationAccounting
from app.adapters.metrics_schema import AdapterMetrics


def test_estimate_upload_download():
    accounting = CommunicationAccounting(profile_name="wifi", compression_enabled=True)
    adapter = AdapterMetrics(
        adapter_id="a1",
        clinic_id="c1",
        version_id="v1",
        communication_round=1,
        parameter_count=100,
        adapter_size_bytes=1000,
        serialized_size_bytes=800,
        compressed_size_bytes=400,
        checksum="hash",
        storage_path="/tmp/test"
    )
    
    assert accounting.estimate_upload(adapter) == 400
    assert accounting.estimate_download(adapter) == 400
    
    # Test uncompressed
    accounting_uncompressed = CommunicationAccounting(profile_name="wifi", compression_enabled=False)
    assert accounting_uncompressed.estimate_upload(adapter) == 800


def test_estimate_latency():
    accounting = CommunicationAccounting(profile_name="wifi")  # 50 MB/s
    latency = accounting.estimate_latency(50 * 1024 * 1024)
    assert latency == 1000.0  # 1000 ms = 1 second
    
    accounting_offline = CommunicationAccounting(profile_name="offline")
    assert accounting_offline.estimate_latency(50 * 1024 * 1024) == 0.0


def test_round_cost():
    accounting = CommunicationAccounting(profile_name="wifi", compression_enabled=True)
    adapter = AdapterMetrics(
        adapter_id="a1",
        clinic_id="c1",
        version_id="v1",
        communication_round=1,
        parameter_count=100,
        adapter_size_bytes=1000,
        serialized_size_bytes=800,
        compressed_size_bytes=400,
        checksum="hash",
        storage_path="/tmp/test"
    )
    
    cost = accounting.estimate_round_cost(num_clients=10, average_adapter=adapter)
    # Upload = 400 * 10 = 4000
    # Download = 400 * 10 = 4000
    # Total = 8000
    assert cost["total_transfer_bytes"] == 8000
