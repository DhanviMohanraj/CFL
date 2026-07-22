"""DriftAdapt ConfigFactory Module.

Author: DriftAdapt Contributors
Purpose: Exposes factory presets for various experiment sizes and deployment setups.
Future Integration: Invoked by experiment orchestrators to load reproducible presets.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config.config_manager import ConfigManager
from app.core.config.exceptions import ConfigurationError
from app.core.config.schema import AppConfig


class ConfigFactory:
    """Factory to generate pre-configured AppConfig settings based on experiment types."""

    # Dictionary containing overrides for each specific experimental preset
    PRESETS: Dict[str, Dict[str, Dict[str, Any]]] = {
        "small_experiment": {
            "system": {"num_workers": 1, "debug": True},
            "training": {"batch_size": 4, "epochs": 1},
            "federated": {"num_clients": 3, "num_rounds": 5},
        },
        "large_experiment": {
            "system": {"num_workers": 8},
            "training": {"batch_size": 16, "epochs": 10},
            "federated": {"num_clients": 50, "num_rounds": 100},
        },
        "debug_experiment": {
            "system": {"debug": True, "num_workers": 0},
            "training": {"batch_size": 2, "epochs": 1},
            "federated": {"num_rounds": 2, "num_clients": 2},
            "logging": {"log_level": "DEBUG"},
        },
        "edge_deployment": {
            "system": {"device": "cpu", "num_workers": 1},
            "model": {"quantization": "4bit"},
            "training": {"batch_size": 2},
            "federated": {"num_clients": 1},
        },
        "research_paper": {
            "training": {"learning_rate": 0.0001, "epochs": 5},
            "federated": {"num_clients": 20, "num_rounds": 200},
            "lora": {"r": 16, "lora_alpha": 32},
        },
    }

    @classmethod
    def create_config(
        cls, preset: str, base_configs_dir: Optional[Path] = None, load_env: bool = True
    ) -> AppConfig:
        """Loads and returns a validated configuration with preset overrides applied.

        Args:
            preset: Name of the preset (small_experiment, large_experiment, etc.).
            base_configs_dir: Optional path containing base YAML config files.
            load_env: If True, merges root environment variables.

        Returns:
            A validated AppConfig instance.

        Raises:
            ConfigurationError: If preset name is unrecognized.
        """
        preset_name = preset.lower().strip()
        if preset_name not in cls.PRESETS:
            valid_keys = ", ".join(cls.PRESETS.keys())
            raise ConfigurationError(
                f"Unknown configuration preset: '{preset}'. Valid presets are: {valid_keys}"
            )

        # 1. Instantiate the base manager
        manager = ConfigManager(configs_dir=base_configs_dir, load_env=load_env)

        # 2. Register preset overrides
        overrides = cls.PRESETS[preset_name]
        manager.apply_runtime_overrides(overrides)

        # 3. Load, override, and return validated configuration
        return manager.get_config()
