"""DriftAdapt LoRA Configuration Manager Unit Tests.

Author: DriftAdapt Contributors
Purpose: Comprehensive unit tests for LoRA configuration loading, merging, validation, and serialization.
"""

import os
import json
from pathlib import Path
import pytest
import tempfile
import yaml

from app.personalization.config.lora_configuration_manager import LoRAConfigurationManager
from app.personalization.config.lora_schema import PersonalizationConfiguration
from app.personalization.config.lora_exceptions import (
    ConfigurationValidationError,
    InvalidRankError,
    InvalidDropoutError,
    InvalidTargetModuleError,
    InvalidPrecisionError,
    InvalidStorageConfigurationError,
)

@pytest.fixture
def clean_manager():
    """Returns a fresh LoRAConfigurationManager and clears state before/after."""
    manager = LoRAConfigurationManager()
    manager.configure_paths(yaml_path=None, json_path=None)
    manager.clear_overrides()
    yield manager
    manager.configure_paths(yaml_path=None, json_path=None)
    manager.clear_overrides()


def test_default_configuration_loading(clean_manager):
    config = clean_manager.load(force_refresh=True)
    assert isinstance(config, PersonalizationConfiguration)
    assert config.lora.rank == 16
    assert config.lora.alpha == 32.0
    assert config.lora.dropout == 0.05
    assert len(config.target_modules.modules) == 7
    assert config.precision.dtype == "bfloat16"
    assert config.training.learning_rate == 2e-4


def test_runtime_override(clean_manager):
    clean_manager.apply_overrides({
        "lora": {"rank": 64},
        "training": {"learning_rate": 5e-5}
    })
    config = clean_manager.load(force_refresh=True)
    assert config.lora.rank == 64
    assert config.training.learning_rate == 5e-5


def test_yaml_loading(clean_manager):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({"lora": {"rank": 8, "dropout": 0.1}}, f)
        temp_path = f.name

    try:
        clean_manager.configure_paths(yaml_path=temp_path)
        config = clean_manager.load(force_refresh=True)
        assert config.lora.rank == 8
        assert config.lora.dropout == 0.1
    finally:
        os.unlink(temp_path)


def test_json_loading(clean_manager):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"lora": {"alpha": 16.0}, "precision": {"dtype": "float32"}}, f)
        temp_path = f.name

    try:
        clean_manager.configure_paths(json_path=temp_path)
        config = clean_manager.load(force_refresh=True)
        assert config.lora.alpha == 16.0
        assert config.precision.dtype == "float32"
    finally:
        os.unlink(temp_path)


def test_environment_variable_override(clean_manager):
    os.environ["DRIFTADAPT__LORA__LORA__RANK"] = "128"
    os.environ["DRIFTADAPT__LORA__TARGET_MODULES__MODULES"] = "q_proj,k_proj"
    
    try:
        config = clean_manager.load(force_refresh=True)
        assert config.lora.rank == 128
        assert config.target_modules.modules == ["q_proj", "k_proj"]
    finally:
        del os.environ["DRIFTADAPT__LORA__LORA__RANK"]
        del os.environ["DRIFTADAPT__LORA__TARGET_MODULES__MODULES"]


def test_validation_invalid_rank(clean_manager):
    clean_manager.apply_overrides({"lora": {"rank": 0}})
    with pytest.raises(InvalidRankError):
        clean_manager.load(force_refresh=True)

    clean_manager.apply_overrides({"lora": {"rank": -5}})
    with pytest.raises(InvalidRankError):
        clean_manager.load(force_refresh=True)


def test_validation_invalid_dropout(clean_manager):
    clean_manager.apply_overrides({"lora": {"dropout": 1.5}})
    with pytest.raises(InvalidDropoutError):
        clean_manager.load(force_refresh=True)


def test_validation_invalid_target_modules(clean_manager):
    clean_manager.apply_overrides({"target_modules": {"modules": []}})
    with pytest.raises(InvalidTargetModuleError):
        clean_manager.load(force_refresh=True)

    clean_manager.apply_overrides({"target_modules": {"modules": ["q_proj", "q_proj"]}})
    with pytest.raises(InvalidTargetModuleError):
        clean_manager.load(force_refresh=True)


def test_validation_invalid_precision(clean_manager):
    clean_manager.apply_overrides({"precision": {"dtype": "float64"}})
    with pytest.raises(InvalidPrecisionError):
        clean_manager.load(force_refresh=True)


def test_validation_storage_paths(clean_manager):
    clean_manager.apply_overrides({"storage": {"adapter_directory": "   "}})
    with pytest.raises(InvalidStorageConfigurationError):
        clean_manager.load(force_refresh=True)


def test_serialization(clean_manager):
    config = clean_manager.load(force_refresh=True)
    cfg_dict = clean_manager.to_dict()
    assert isinstance(cfg_dict, dict)
    assert cfg_dict["lora"]["rank"] == 16
    
    digest = clean_manager.get_hash_digest()
    assert isinstance(digest, str)
    assert len(digest) == 64  # SHA-256


def test_exporting(clean_manager):
    with tempfile.TemporaryDirectory() as td:
        yaml_path = Path(td) / "export.yaml"
        json_path = Path(td) / "export.json"
        
        clean_manager.export_to_yaml(yaml_path)
        clean_manager.export_to_json(json_path)
        
        assert yaml_path.exists()
        assert json_path.exists()
        
        with open(yaml_path, "r") as yf:
            y_data = yaml.safe_load(yf)
            assert y_data["lora"]["rank"] == 16
            
        with open(json_path, "r") as jf:
            j_data = json.load(jf)
            assert j_data["lora"]["rank"] == 16
