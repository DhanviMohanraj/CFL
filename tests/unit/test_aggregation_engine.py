"""Unit Tests for Aggregation Engine (Module 2.6).

Author: DriftAdapt Contributors
"""

import pytest
import torch
import io
from typing import Dict, Any

from app.schemas.client_update_record import ClientUpdateRecord
from app.schemas.aggregation_request import AggregationRequest
from app.services.aggregation.fedavg_service import FedAvgService
from app.services.aggregation.weighted_fedavg import WeightedFedAvgService
from app.services.aggregation.update_validator import UpdateValidator
from app.services.aggregation.update_filter import UpdateFilter
from app.services.aggregation.conflict_detector import ConflictDetector
from app.services.aggregation.adapter_merger import AdapterMerger
from app.services.aggregation.version_manager import VersionManager
from app.services.aggregation.aggregation_history import AggregationHistory
from app.services.aggregation.aggregation_registry import AggregationRegistry
from app.services.aggregation.aggregation_metrics import AggregationMetrics
from app.services.aggregation.aggregation_engine import AggregationEngine
from app.services.federation.checksum_service import ChecksumService


@pytest.fixture
def dummy_state_dict() -> Dict[str, Any]:
    """Returns a simple state dict with one tensor."""
    return {
        "lora_A.weight": torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float32)
    }


@pytest.fixture
def dummy_payload(dummy_state_dict: Dict[str, Any]) -> bytes:
    """Serializes the dummy state dict to bytes."""
    buffer = io.BytesIO()
    torch.save(dummy_state_dict, buffer)
    return buffer.getvalue()


def test_fedavg_service(dummy_state_dict: Dict[str, Any]) -> None:
    """Tests classical FedAvg equal weighting."""
    service = FedAvgService()
    
    # Create a second client with doubled weights
    client2_sd = {
        "lora_A.weight": torch.tensor([[3.0, 4.0], [5.0, 6.0]], dtype=torch.float32)
    }
    
    aggregated = service.aggregate(
        state_dicts=[dummy_state_dict, client2_sd],
        weights=[1.0, 1.0] # Weights are ignored in uniform FedAvgService
    )
    
    expected = torch.tensor([[2.0, 3.0], [4.0, 5.0]], dtype=torch.float32)
    assert torch.allclose(aggregated["lora_A.weight"], expected)


def test_weighted_fedavg_service(dummy_state_dict: Dict[str, Any]) -> None:
    """Tests weighted FedAvg."""
    service = WeightedFedAvgService()
    
    client2_sd = {
        "lora_A.weight": torch.tensor([[3.0, 4.0], [5.0, 6.0]], dtype=torch.float32)
    }
    
    # Give client 2 three times the weight
    aggregated = service.aggregate(
        state_dicts=[dummy_state_dict, client2_sd],
        weights=[1.0, 3.0]
    )
    
    # Expected: (1 * [1,2,3,4] + 3 * [3,4,5,6]) / 4
    # = ([1,2,3,4] + [9,12,15,18]) / 4
    # = [10,14,18,22] / 4
    # = [2.5, 3.5, 4.5, 5.5]
    expected = torch.tensor([[2.5, 3.5], [4.5, 5.5]], dtype=torch.float32)
    assert torch.allclose(aggregated["lora_A.weight"], expected)


def test_update_filter() -> None:
    """Tests duplicate and stale update rejection."""
    filter_svc = UpdateFilter()
    
    updates = [
        ClientUpdateRecord(client_id="client1", adapter_id="ad1", upload_timestamp=10.0, personalization_round=1, checksum="a"),
        ClientUpdateRecord(client_id="client1", adapter_id="ad2", upload_timestamp=20.0, personalization_round=1, checksum="b"), # Duplicate, keeps this one
        ClientUpdateRecord(client_id="client2", adapter_id="ad3", upload_timestamp=15.0, personalization_round=0, checksum="c"), # Stale
    ]
    
    accepted, rejected = filter_svc.filter_updates(updates, expected_round=1)
    
    assert len(accepted) == 1
    assert accepted[0].client_id == "client1"
    assert accepted[0].adapter_id == "ad2"  # Kept the latest one
    
    assert len(rejected) == 2
    assert rejected[0].validation_status == "STALE"
    assert rejected[1].validation_status == "DUPLICATE"


def test_conflict_detector() -> None:
    """Tests conflict detection logic."""
    detector = ConflictDetector()
    
    updates = [
        ClientUpdateRecord(client_id="client1", adapter_id="ad1", personalization_round=2, dataset_size=100, checksum="a", upload_timestamp=10.0),
        ClientUpdateRecord(client_id="client2", adapter_id="ad2", personalization_round=2, dataset_size=150, checksum="b", upload_timestamp=11.0),
    ]
    
    # Normal case
    assert not detector.detect_conflicts(updates, current_global_round=2)
    
    # Server mismatch case
    conflicts = detector.detect_conflicts(updates, current_global_round=1)
    assert len(conflicts) == 1
    assert "target rounds {2}" in conflicts[0]


def test_version_manager() -> None:
    """Tests version generation and rollback."""
    vm = VersionManager()
    v1 = vm.generate_next_version(1)
    v2 = vm.generate_next_version(2)
    
    assert v1 == "v1.0.0-round1"
    assert v2 == "v1.0.0-round2"
    assert vm.get_latest_version() == v2
    
    rolled_back = vm.rollback_version()
    assert rolled_back == v1
    assert vm.get_latest_version() == v1


def test_aggregation_engine_success(dummy_payload: bytes) -> None:
    """Tests full engine integration."""
    checksum_svc = ChecksumService()
    engine = AggregationEngine(
        update_validator=UpdateValidator(checksum_service=checksum_svc),
        update_filter=UpdateFilter(),
        conflict_detector=ConflictDetector(),
        adapter_merger=AdapterMerger(),
        version_manager=VersionManager(),
        aggregation_history=AggregationHistory(),
        aggregation_registry=AggregationRegistry(),
        aggregation_metrics=AggregationMetrics()
    )
    
    # Calculate proper checksum for payload
    valid_checksum, _ = checksum_svc.generate_checksum(dummy_payload)
    
    record1 = ClientUpdateRecord(
        client_id="client1",
        adapter_id="ad1",
        local_epoch=1,
        personalization_round=1,
        dataset_size=100,
        update_weight=1.0,
        checksum=valid_checksum,
        upload_timestamp=10.0
    )
    
    record2 = ClientUpdateRecord(
        client_id="client2",
        adapter_id="ad2",
        local_epoch=1,
        personalization_round=1,
        dataset_size=150,
        update_weight=1.0,
        checksum=valid_checksum,
        upload_timestamp=11.0
    )
    
    # Submit updates
    engine.submit_client_update(record1, dummy_payload)
    engine.submit_client_update(record2, dummy_payload)
    
    req = AggregationRequest(
        communication_round=1,
        aggregation_algorithm="fedavg",
        minimum_clients=2,
        aggregation_timestamp=12.0
    )
    
    result = engine.run_aggregation(req)
    
    assert result.success is True
    assert result.global_adapter_version == "v1.0.0-round1"
    assert len(result.aggregated_clients) == 2
    assert result.aggregation_statistics.efficiency == 1.0 if hasattr(result.aggregation_statistics, "efficiency") else True
