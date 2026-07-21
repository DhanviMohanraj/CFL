"""DriftAdapt Config Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies the configuration manager loader, validations, overrides, and environment checks.
Future Integration: Executed as part of the test suite in CI.
"""

from pathlib import Path
import pytest
from app.core.config import (
    ConfigManager,
    ConfigFactory,
    AppConfig,
    ValidationError,
    ConfigurationError,
    get_project_root,
)


def test_project_root_resolution() -> None:
    """Verifies that project root resolves correctly."""
    root = get_project_root()
    assert root.exists()
    assert (root / "configs").exists()
    assert (root / "app").exists()


def test_default_config_fallback(tmp_path: Path) -> None:
    """Verifies that ConfigManager falls back to defaults if YAML files are missing."""
    empty_configs_dir = tmp_path / "configs"
    empty_configs_dir.mkdir()

    manager = ConfigManager(configs_dir=empty_configs_dir, load_env=False)
    config = manager.get_config()

    assert isinstance(config, AppConfig)
    assert config.system.project_name == "DriftAdapt"
    assert config.model.max_seq_length == 512
    assert config.training.batch_size == 8


def test_load_valid_yaml_configs() -> None:
    """Verifies that YAML files inside configs/ are successfully loaded."""
    manager = ConfigManager(load_env=False)
    config = manager.get_config()

    assert config.system.project_name == "DriftAdapt"
    assert config.model.max_seq_length == 512
    assert config.lora.r == 8
    assert config.training.learning_rate == 0.0002
    assert config.federated.num_clients == 10
    assert config.dataset.dataset_name == "MIMIC-IV-Advisory"
    assert config.drift.drift_detector == "adwin"
    assert config.evaluation.evaluation_frequency == 5
    assert config.logging.log_level == "INFO"
    assert config.experiment.experiment_name == "baseline_personalization"


def test_validation_constraints() -> None:
    """Verifies that invalid values trigger custom ValidationError."""
    manager = ConfigManager(load_env=False)

    # 1. Test negative learning rate
    manager.apply_runtime_overrides({"training": {"learning_rate": -0.01}})
    with pytest.raises(ValidationError):
        manager.get_config()
    manager.clear_overrides()

    # 2. Test negative batch size
    manager.apply_runtime_overrides({"training": {"batch_size": 0}})
    with pytest.raises(ValidationError):
        manager.get_config()
    manager.clear_overrides()

    # 3. Test invalid device
    manager.apply_runtime_overrides({"system": {"device": "invalid_device"}})
    with pytest.raises(ValidationError):
        manager.get_config()
    manager.clear_overrides()


def test_runtime_overrides() -> None:
    """Verifies programmatic runtime overrides."""
    manager = ConfigManager(load_env=False)

    overrides = {
        "training": {"learning_rate": 0.005, "batch_size": 16},
        "system": {"debug": True},
    }
    manager.apply_runtime_overrides(overrides)
    config = manager.get_config()

    assert config.training.learning_rate == 0.005
    assert config.training.batch_size == 16
    assert config.system.debug is True

    # Test clearing overrides
    manager.clear_overrides()
    config_cleared = manager.get_config()
    assert config_cleared.training.learning_rate == 0.0002
    assert config_cleared.training.batch_size == 8
    assert config_cleared.system.debug is False


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies that environment variables override YAML and runtime settings."""
    monkeypatch.setenv("MODEL_NAME", "custom-llama")
    monkeypatch.setenv("DEVICE", "cpu")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OUTPUT_DIR", "./test_results")

    monkeypatch.setenv("DRIFTADAPT_TRAINING__LEARNING_RATE", "0.009")

    manager = ConfigManager(load_env=False)
    config = manager.get_config()

    assert config.model.foundation_model == "custom-llama"
    assert config.system.device == "cpu"
    assert config.system.debug is True
    assert config.logging.log_level == "DEBUG"
    assert config.evaluation.output_dir == "./test_results"
    assert config.training.learning_rate == 0.009


def test_factory_presets() -> None:
    """Verifies that factory presets are correctly instantiated with proper values."""
    small_config = ConfigFactory.create_config("small_experiment", load_env=False)
    assert small_config.training.epochs == 1
    assert small_config.training.batch_size == 4
    assert small_config.federated.num_clients == 3
    assert small_config.system.num_workers == 1

    edge_config = ConfigFactory.create_config("edge_deployment", load_env=False)
    assert edge_config.system.device == "cpu"
    assert edge_config.model.quantization == "4bit"
    assert edge_config.training.batch_size == 2
    assert edge_config.federated.num_clients == 1

    with pytest.raises(ConfigurationError):
        ConfigFactory.create_config("invalid_preset", load_env=False)
