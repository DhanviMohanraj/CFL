"""DriftAdapt ConfigManager Module.

Author: DriftAdapt Contributors
Purpose: Orchestrates config lifecycle: reading, merging, overriding, caching, and exposing schemas.
Future Integration: Central source of configurations for all system components.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import threading

from app.core.config.exceptions import ConfigurationError
from app.core.config.loader import (
    load_raw_configurations,
    apply_env_overrides,
    load_env_file,
)
from app.core.config.validator import validate_configuration
from app.core.config.schema import AppConfig


class ConfigManager:
    """Centralized configuration manager supporting lazy loading, overrides, and validation.

    This manager is thread-safe and implements thread caching of validated configurations.
    """

    def __init__(self, configs_dir: Optional[Path] = None, load_env: bool = True) -> None:
        """Initializes the ConfigManager.

        Args:
            configs_dir: Directory containing the YAML config files.
            load_env: If True, loads variables from root .env.
        """
        self._configs_dir: Optional[Path] = configs_dir
        self._load_env: bool = load_env
        self._runtime_overrides: Dict[str, Any] = {}
        self._config: Optional[AppConfig] = None
        self._lock = threading.Lock()

    def get_config(self) -> AppConfig:
        """Retrieves the strongly-typed configuration instance.

        Performs thread-safe lazy loading and caching.
        """
        if self._config is not None:
            return self._config

        with self._lock:
            # Double-check lock pattern
            if self._config is not None:
                return self._config  # type: ignore[unreachable]

            self._config = self._load_and_validate()
            return self._config

    def apply_runtime_overrides(self, overrides: Dict[str, Any]) -> None:
        """Applies programmatic runtime overrides to target configuration fields.

        Clears cached configuration immediately. Format is nested dictionary:
        e.g. {"training": {"learning_rate": 1e-5}, "system": {"debug": True}}
        """
        with self._lock:
            for section, values in overrides.items():
                if not isinstance(values, dict):
                    raise ConfigurationError(
                        f"Runtime override section must be a dictionary. Got {type(values)} for section '{section}'"
                    )
                self._runtime_overrides.setdefault(section, {}).update(values)
            # Invalidate cache
            self._config = None

    def clear_overrides(self) -> None:
        """Clears all registered runtime overrides and invalidates cached configuration."""
        with self._lock:
            self._runtime_overrides.clear()
            self._config = None

    def refresh(self) -> AppConfig:
        """Forces reloading configurations from files, environment variables, and overrides."""
        with self._lock:
            self._config = None
            self._config = self._load_and_validate()
            return self._config

    def _load_and_validate(self) -> AppConfig:
        """Performs raw loading, env-parsing, runtime override, and schema validations."""
        # 1. Load env file
        if self._load_env:
            load_env_file()

        # 2. Load and merge YAML files + default templates
        raw_dict = load_raw_configurations(self._configs_dir)

        # 3. Apply runtime overrides
        if self._runtime_overrides:
            for section, values in self._runtime_overrides.items():
                raw_dict.setdefault(section, {}).update(values)

        # 4. Apply environment overrides (higher priority than YAML and runtime overrides)
        # Note: Environment overrides take precedence over everything else.
        raw_dict = apply_env_overrides(raw_dict)

        # 5. Validate structure and return Pydantic object
        return validate_configuration(raw_dict)
