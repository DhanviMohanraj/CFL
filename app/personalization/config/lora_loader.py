"""DriftAdapt Personalization LoRA Configuration Loader.

Author: DriftAdapt Contributors
Purpose: Loads configuration from defaults, JSON, YAML, environment variables, and runtime overrides.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import yaml

from app.personalization.config.lora_defaults import DEFAULT_LORA_CONFIGURATION


class LoRAConfigurationLoader:
    """Loads and merges configuration from various sources according to hierarchy rules."""

    @classmethod
    def load_and_merge(
        cls,
        yaml_path: str | Path | None = None,
        json_path: str | Path | None = None,
        runtime_overrides: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Loads and merges configuration sources in priority order.
        
        Priority: Runtime Overrides > Environment Variables > YAML > JSON > Defaults.
        
        Args:
            yaml_path: Path to a YAML configuration file.
            json_path: Path to a JSON configuration file.
            runtime_overrides: Dictionary of runtime overrides.
            
        Returns:
            Merged dictionary.
        """
        # 1. Start with defaults (deep copy to avoid mutating the constant)
        merged_config = cls._deep_merge({}, DEFAULT_LORA_CONFIGURATION)

        # 2. Load JSON if provided
        if json_path and Path(json_path).exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                merged_config = cls._deep_merge(merged_config, json_data)

        # 3. Load YAML if provided
        if yaml_path and Path(yaml_path).exists():
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
                if yaml_data:
                    merged_config = cls._deep_merge(merged_config, yaml_data)

        # 4. Apply environment overrides
        env_overrides = cls._extract_env_overrides()
        merged_config = cls._deep_merge(merged_config, env_overrides)

        # 5. Apply runtime overrides
        if runtime_overrides:
            merged_config = cls._deep_merge(merged_config, runtime_overrides)

        return merged_config

    @classmethod
    def _extract_env_overrides(cls) -> Dict[str, Any]:
        """Extracts and parses environment variables starting with DRIFTADAPT__LORA__.
        
        Example: DRIFTADAPT__LORA__TRAINING__LEARNING_RATE=1e-4 -> {"training": {"learning_rate": 0.0001}}
        """
        env_prefix = "DRIFTADAPT__LORA__"
        overrides: Dict[str, Any] = {}

        for key, value in os.environ.items():
            if not key.startswith(env_prefix):
                continue

            # Strip prefix and split by __
            path = key[len(env_prefix):].lower().split("__")
            
            # Navigate/create nested dictionaries
            current = overrides
            for idx, part in enumerate(path):
                if idx == len(path) - 1:
                    current[part] = cls._parse_env_value(value)
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

        return overrides

    @staticmethod
    def _parse_env_value(value: str) -> Any:
        """Heuristically parses an environment string into python types."""
        v_lower = value.strip().lower()
        if v_lower in ("true", "1", "yes"):
            return True
        if v_lower in ("false", "0", "no"):
            return False
        if v_lower == "none":
            return None
        
        try:
            return int(value)
        except ValueError:
            pass
            
        try:
            return float(value)
        except ValueError:
            pass
            
        # Comma-separated list check (basic support)
        if "," in value:
            return [part.strip() for part in value.split(",")]
            
        return value

    @staticmethod
    def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merges overlay dictionary into base dictionary."""
        result = dict(base)
        for k, v in overlay.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = LoRAConfigurationLoader._deep_merge(result[k], v)
            else:
                result[k] = v
        return result
