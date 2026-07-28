"""DriftAdapt LoRA Services Unit Tests.

Author: DriftAdapt Contributors
Purpose: Validates the LoRA API layer services (ConfigBuilder, Registry, Metadata).
"""

import pytest
from app.schemas.lora_config import LoRAConfigurationRequest
from app.schemas.adapter_metadata import AdapterMetadataResponse
from app.services.lora.config_builder import ConfigBuilder
from app.services.lora.adapter_registry import AdapterRegistry
from app.services.lora.metadata_service import MetadataService
from app.services.lora.target_module_selector import TargetModuleSelector
from unittest.mock import MagicMock


def test_config_builder_normalization():
    builder = ConfigBuilder()
    req = LoRAConfigurationRequest(
        adapter_name="test_adapter",
        r=16,
        lora_alpha=32.0,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"]
    )
    
    internal_config = builder.build_configuration(req)
    
    assert internal_config.adapter.name == "test_adapter"
    assert internal_config.lora.rank == 16
    assert internal_config.lora.alpha == 32.0
    assert internal_config.lora.dropout == 0.1
    assert "q_proj" in internal_config.target_modules.modules


def test_adapter_registry_lifecycle():
    registry = AdapterRegistry()
    
    meta = AdapterMetadataResponse(
        adapter_id="123",
        adapter_name="test",
        creation_timestamp="2026",
        model_name="qwen",
        parameter_count=1000,
        trainable_parameters=10,
        frozen_parameters=990,
        adapter_rank=8,
        adapter_alpha=16.0,
        adapter_dropout=0.05
    )
    
    # Register
    registry.register(meta)
    
    # Duplicate should fail
    with pytest.raises(ValueError):
        registry.register(meta)
        
    # List and Get
    assert len(registry.list_adapters()) == 1
    fetched = registry.get_adapter("123")
    assert fetched is not None
    assert fetched.adapter_name == "test"
    
    # Unregister
    assert registry.unregister("123") is True
    assert registry.unregister("123") is False


def test_metadata_service_statistics():
    registry = AdapterRegistry()
    meta = AdapterMetadataResponse(
        adapter_id="456",
        adapter_name="eff_test",
        creation_timestamp="2026",
        model_name="qwen",
        parameter_count=1000,
        trainable_parameters=50,
        frozen_parameters=950,
        adapter_rank=8,
        adapter_alpha=16.0,
        adapter_dropout=0.05,
        target_modules=["a", "b"]
    )
    registry.register(meta)
    
    metadata_service = MetadataService(registry)
    stats = metadata_service.get_adapter_statistics("456")
    
    assert stats["trainable_parameters"] == 50
    assert stats["percentage_trainable"] == 5.0  # 50 / 1000 * 100
    assert stats["target_layers"] == 2
    
    with pytest.raises(KeyError):
        metadata_service.get_adapter_statistics("missing")


def test_target_module_selector():
    selector = TargetModuleSelector()
    
    # Create a dummy model
    mock_model = MagicMock()
    mock_model.named_modules.return_value = [
        ("model.layers.0.self_attn.q_proj", None),
        ("model.layers.0.self_attn.k_proj", None),
        ("model.layers.0.mlp.gate_proj", None),
        ("model.layers.0.random_layer", None)
    ]
    
    modules = selector.discover_modules(mock_model, include_mlp=True)
    assert set(modules) == {"q_proj", "k_proj", "gate_proj"}
    
    modules_no_mlp = selector.discover_modules(mock_model, include_mlp=False)
    assert set(modules_no_mlp) == {"q_proj", "k_proj"}
