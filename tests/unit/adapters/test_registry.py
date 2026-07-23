"""Unit tests for the Federated Adapter Registry.

Author: DriftAdapt Contributors
"""

import json
import threading
from pathlib import Path

import pytest

from app.adapters.adapter_info import AdapterInfo
from app.adapters.enums import AdapterStatus
from app.adapters.exceptions import (
    AdapterAlreadyExists,
    AdapterNotFound,
    ClinicNotFound,
    InvalidClinicID,
    RegistryPersistenceError,
)
from app.adapters.registry import AdapterRegistry


@pytest.fixture(autouse=True)
def reset_singleton():
    """Ensure Singleton state is reset between tests."""
    AdapterRegistry._instance = None
    yield
    AdapterRegistry._instance = None


@pytest.fixture
def registry(tmp_path: Path):
    """Fixture providing a fresh AdapterRegistry with a temp file."""
    reg = AdapterRegistry()
    reg._registry_path = tmp_path / "registry.json"
    reg._autosave = True
    reg._backup = False
    reg.clear()
    return reg


def test_register_adapter(registry: AdapterRegistry):
    """Test standard adapter registration."""
    info = registry.register("clinic_001", "my_adapter", 1, {"meta": "data"})
    assert info.clinic_id == "clinic_001"
    assert info.adapter_name == "my_adapter"
    assert info.round_number == 1
    assert info.status == AdapterStatus.REGISTERED
    assert info.metadata["meta"] == "data"
    
    # Retrieve
    retrieved = registry.get(adapter_id=info.adapter_id)
    assert retrieved.adapter_id == info.adapter_id

    # Retrieve by clinic and name
    retrieved2 = registry.get(clinic_id="clinic_001", adapter_name="my_adapter")
    assert retrieved2.adapter_id == info.adapter_id


def test_invalid_clinic_id(registry: AdapterRegistry):
    """Test validation of clinic ID."""
    with pytest.raises(InvalidClinicID):
        registry.register("", "adapter", 1)
    
    with pytest.raises(InvalidClinicID):
        registry.register("None", "adapter", 1)

    with pytest.raises(InvalidClinicID):
        registry.register("clinic 01!", "adapter", 1)


def test_duplicate_registration(registry: AdapterRegistry):
    """Test duplicate registration constraint."""
    registry.register("clinic_001", "duplicate_adapter", 1)
    
    with pytest.raises(AdapterAlreadyExists):
        registry.register("clinic_001", "duplicate_adapter", 1)


def test_activate_adapter(registry: AdapterRegistry):
    """Test adapter activation constraints."""
    ad1 = registry.register("clinic_001", "adapter1", 1)
    ad2 = registry.register("clinic_001", "adapter2", 2)
    
    # Activate 1
    registry.activate(ad1.adapter_id)
    assert registry.get(adapter_id=ad1.adapter_id).is_active is True
    assert registry.get(adapter_id=ad2.adapter_id).is_active is False
    
    # Activate 2
    registry.activate(ad2.adapter_id)
    assert registry.get(adapter_id=ad1.adapter_id).is_active is False
    assert registry.get(adapter_id=ad2.adapter_id).is_active is True


def test_delete_adapter(registry: AdapterRegistry):
    """Test soft deletion."""
    ad = registry.register("clinic_001", "adapter_to_delete", 1)
    registry.activate(ad.adapter_id)
    assert registry.get(adapter_id=ad.adapter_id).is_active is True
    
    registry.delete(ad.adapter_id)
    
    # Should not be found by normal lookup if deleted, but get by ID returns deleted check
    with pytest.raises(AdapterNotFound):
        registry.get(adapter_id=ad.adapter_id)
        
    # Check internal status directly
    assert registry._adapters[ad.adapter_id].status == AdapterStatus.DELETED
    assert registry._adapters[ad.adapter_id].is_active is False


def test_latest_adapter(registry: AdapterRegistry):
    """Test getting latest adapter for clinic."""
    registry.register("clinic_001", "v1", 1)
    registry.register("clinic_001", "v3", 3)
    registry.register("clinic_001", "v2", 2)
    
    latest = registry.get_latest("clinic_001")
    assert latest.round_number == 3
    assert latest.adapter_name == "v3"
    
    with pytest.raises(ClinicNotFound):
        registry.get_latest("clinic_999")


def test_persistence_save_load(registry: AdapterRegistry):
    """Test JSON persistence."""
    ad1 = registry.register("clinic_1", "ad1", 1)
    registry.activate(ad1.adapter_id)
    
    assert registry._registry_path.exists()
    
    # Clear memory
    registry.clear()
    assert len(registry.list_all()) == 0
    
    # Load from disk
    registry.load_registry()
    assert len(registry.list_all()) == 1
    
    loaded_ad = registry.get(adapter_id=ad1.adapter_id)
    assert loaded_ad.is_active is True
    assert loaded_ad.clinic_id == "clinic_1"


def test_export_import(registry: AdapterRegistry):
    """Test export and import functionality."""
    registry.register("c1", "a1", 1)
    registry.register("c2", "a2", 2)
    
    data = registry.export_registry()
    assert "adapters" in data
    assert len(data["adapters"]) == 2
    
    # New registry
    reg2 = AdapterRegistry()
    reg2.import_registry(data)
    assert len(reg2.list_all()) == 2
    
    # Cleanup singleton again explicitly
    AdapterRegistry._instance = None


def test_statistics(registry: AdapterRegistry):
    """Test statistics calculation."""
    # 2 Clinics, 3 Adapters (1 active, 1 inactive, 1 deleted)
    ad1 = registry.register("c1", "a1", 1)
    ad2 = registry.register("c1", "a2", 2)
    ad3 = registry.register("c2", "a3", 1)
    
    registry.activate(ad1.adapter_id)
    registry.delete(ad3.adapter_id)
    
    stats = registry.statistics()
    assert stats["total_clinics"] == 1  # c2 has no non-deleted adapters
    assert stats["total_adapters"] == 3
    assert stats["active_adapters"] == 1
    assert stats["deleted_adapters"] == 1
    assert stats["latest_round"] == 2
    assert stats["average_adapters_per_clinic"] == 2.0


def test_concurrent_registration(registry: AdapterRegistry):
    """Test thread-safety for concurrent registration."""
    def register_task(index: int):
        registry.register(f"clinic_{index % 10}", f"adapter_{index}", index + 1)
        
    threads = []
    for i in range(100):
        t = threading.Thread(target=register_task, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    assert len(registry.list_all()) == 100
    stats = registry.statistics()
    assert stats["total_adapters"] == 100
    assert stats["total_clinics"] == 10
