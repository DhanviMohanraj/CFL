"""DriftAdapt PEFT Integration Layer Unit Tests.

Author: DriftAdapt Contributors
Purpose: Validates that adapters are safely injected into frozen PyTorch models, retaining structural invariants.
"""

import pytest
import torch
import torch.nn as nn
from unittest.mock import patch, MagicMock

from app.personalization.config.lora_configuration_manager import LoRAConfigurationManager
from app.personalization.config.lora_schema import PersonalizationConfiguration
from app.personalization.peft.peft_exceptions import (
    TargetModuleNotFoundError,
    FrozenModelViolationError,
    AdapterValidationError,
    PEFTIntegrationError
)
from app.personalization.peft.peft_manager import PEFTManager
from app.personalization.peft.adapter_validator import AdapterValidator
from app.personalization.peft.parameter_inspector import ParameterInspector


# ---------------------------------------------------------
# DUMMY MODEL ARCHITECTURE FOR TESTING
# ---------------------------------------------------------
class DummyLinear(nn.Module):
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features))

class DummyTransformerBlock(nn.Module):
    def __init__(self):
        super().__init__()
        self.q_proj = DummyLinear(16, 16)
        self.k_proj = DummyLinear(16, 16)
        self.v_proj = DummyLinear(16, 16)
        self.o_proj = DummyLinear(16, 16)

class DummyFoundationModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(100, 16)
        self.blocks = nn.ModuleList([DummyTransformerBlock() for _ in range(2)])
        self.lm_head = DummyLinear(16, 100)
        
    def forward(self, x):
        pass


@pytest.fixture
def frozen_dummy_model():
    model = DummyFoundationModel()
    for param in model.parameters():
        param.requires_grad = False
    return model


@pytest.fixture
def unfrozen_dummy_model():
    model = DummyFoundationModel()
    for param in model.parameters():
        param.requires_grad = True
    return model


@pytest.fixture
def clean_peft_manager():
    """Returns a clean PEFTManager."""
    manager = PEFTManager()
    manager._peft_model = None
    manager._metadata = None
    yield manager
    manager._peft_model = None
    manager._metadata = None


# ---------------------------------------------------------
# UNIT TESTS
# ---------------------------------------------------------

def test_verify_frozen_base_success(frozen_dummy_model):
    # Should not raise
    AdapterValidator.verify_frozen_base(frozen_dummy_model)


def test_verify_frozen_base_failure(unfrozen_dummy_model):
    with pytest.raises(FrozenModelViolationError):
        AdapterValidator.verify_frozen_base(unfrozen_dummy_model)


def test_target_modules_found(frozen_dummy_model):
    # Should not raise
    AdapterValidator.verify_target_modules_exist(frozen_dummy_model, ["q_proj", "v_proj"])


def test_target_modules_not_found(frozen_dummy_model):
    with pytest.raises(TargetModuleNotFoundError):
        AdapterValidator.verify_target_modules_exist(frozen_dummy_model, ["non_existent_proj"])


def test_parameter_inspector_frozen(frozen_dummy_model):
    info = ParameterInspector.inspect(frozen_dummy_model)
    assert info["trainable_parameters"] == 0
    assert info["trainable_ratio"] == 0.0
    assert info["total_parameters"] > 0


@patch("app.personalization.peft.peft_manager.ModelManager")
def test_peft_manager_integration(mock_model_manager_cls, frozen_dummy_model, clean_peft_manager):
    # Setup mock ModelManager to return our dummy model
    mock_instance = MagicMock()
    mock_instance.get_model.return_value = frozen_dummy_model
    mock_model_manager_cls.return_value = mock_instance

    # We need to apply overrides to the ConfigManager to ensure target modules match our dummy model
    config_mgr = LoRAConfigurationManager()
    config_mgr.clear_overrides()
    config_mgr.apply_overrides({
        "target_modules": {"modules": ["q_proj", "v_proj"]},
        "lora": {"rank": 4, "alpha": 8.0}
    })

    # Perform injection
    try:
        peft_model = clean_peft_manager.initialize_adapter(force_refresh=True)
    except ImportError:
        pytest.skip("PEFT library not installed, skipping injection test.")

    # Validation
    assert peft_model is not None
    
    # Check Metadata
    metadata = clean_peft_manager.get_metadata()
    assert metadata.rank == 4
    assert metadata.alpha == 8.0
    assert "q_proj" in metadata.target_modules
    assert metadata.trainable_parameters > 0
    assert metadata.total_parameters > metadata.trainable_parameters
    assert metadata.trainable_ratio > 0.0

    # Ensure get_model returns the same instance
    assert clean_peft_manager.get_model() is peft_model


@patch("app.personalization.peft.peft_manager.ModelManager")
def test_peft_manager_unfrozen_base_fails(mock_model_manager_cls, unfrozen_dummy_model, clean_peft_manager):
    # Setup mock ModelManager to return an unfrozen model
    mock_instance = MagicMock()
    mock_instance.get_model.return_value = unfrozen_dummy_model
    mock_model_manager_cls.return_value = mock_instance

    config_mgr = LoRAConfigurationManager()
    config_mgr.clear_overrides()

    try:
        with pytest.raises(FrozenModelViolationError):
            clean_peft_manager.initialize_adapter(force_refresh=True)
    except ImportError:
        pytest.skip("PEFT library not installed, skipping injection test.")
