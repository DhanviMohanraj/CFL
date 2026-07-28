"""DriftAdapt Personalization LoRA Configuration Manager.

Author: DriftAdapt Contributors
Purpose: Exposes a singleton configuration manager for LoRA personalization that handles loading, validation, and serialization.
"""

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from pydantic import ValidationError

from app.core.logging import LoggerFactory
from app.core.metrics import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType
from app.core.metrics.exceptions import MetricAlreadyExists

from app.personalization.config.lora_schema import PersonalizationConfiguration
from app.personalization.config.lora_loader import LoRAConfigurationLoader
from app.personalization.config.lora_validator import LoRAConfigurationValidator
from app.personalization.config.lora_exceptions import ConfigurationValidationError


class LoRAConfigurationManager:
    """Thread-safe Singleton manager for Personalization Configuration."""

    _instance: Optional['LoRAConfigurationManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'LoRAConfigurationManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LoRAConfigurationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Prevent re-initialization if already instantiated
        if not hasattr(self, "_initialized"):
            self._logger = LoggerFactory.get_logger("LoRAConfigurationManager")
            self._metrics = MetricsBus()
            self._register_metrics()
            self._config: Optional[PersonalizationConfiguration] = None
            self._runtime_overrides: Dict[str, Any] = {}
            self._yaml_path: Optional[str | Path] = None
            self._json_path: Optional[str | Path] = None
            self._initialized = True

    def _register_metrics(self) -> None:
        metrics = [
            ("lora.config.load_time_ms", MetricType.SYSTEM, "Time taken to load config in ms"),
            ("lora.rank", MetricType.SYSTEM, "LoRA rank value"),
            ("lora.alpha", MetricType.SYSTEM, "LoRA alpha value"),
            ("lora.dropout", MetricType.SYSTEM, "LoRA dropout value"),
            ("lora.target_module_count", MetricType.SYSTEM, "Number of LoRA target modules"),
            ("lora.training.learning_rate", MetricType.SYSTEM, "Training learning rate")
        ]
        for name, mtype, desc in metrics:
            try:
                self._metrics.register_schema(name, mtype, desc)
            except MetricAlreadyExists:
                pass

    def configure_paths(self, yaml_path: str | Path | None = None, json_path: str | Path | None = None) -> None:
        """Sets the file paths to load configurations from."""
        with self._lock:
            self._yaml_path = yaml_path
            self._json_path = json_path
            self._config = None  # Invalidate cache

    def apply_overrides(self, overrides: Dict[str, Any]) -> None:
        """Applies programmatic runtime overrides and invalidates cache."""
        with self._lock:
            self._runtime_overrides = LoRAConfigurationLoader._deep_merge(self._runtime_overrides, overrides)
            self._config = None
            self._logger.info("Applied runtime overrides to LoRA configuration.", overrides=overrides)

    def clear_overrides(self) -> None:
        """Clears all programmatic runtime overrides and invalidates cache."""
        with self._lock:
            self._runtime_overrides.clear()
            self._config = None
            self._logger.info("Cleared runtime overrides for LoRA configuration.")

    def load(self, force_refresh: bool = False) -> PersonalizationConfiguration:
        """Loads, merges, validates, and returns the configuration object.
        
        Args:
            force_refresh: If True, bypasses the cache and forces a full reload.
        """
        if self._config is not None and not force_refresh:
            return self._config

        with self._lock:
            if self._config is not None and not force_refresh:
                return self._config

            start_time = time.perf_counter()

            # 1. Load and Merge
            raw_dict = LoRAConfigurationLoader.load_and_merge(
                yaml_path=self._yaml_path,
                json_path=self._json_path,
                runtime_overrides=self._runtime_overrides
            )
            self._logger.debug("LoRA configuration raw dictionary merged successfully.")

            # 2. Domain Validation
            LoRAConfigurationValidator.validate(raw_dict)
            self._logger.debug("LoRA configuration passed pre-instantiation domain validation.")

            # 3. Pydantic Instantiation (Strong Typing)
            try:
                config_obj = PersonalizationConfiguration(**raw_dict)
            except ValidationError as e:
                self._logger.error("Failed to parse LoRA configuration via Pydantic schema.", error=str(e))
                raise ConfigurationValidationError(f"Pydantic schema validation failed: {e}") from e

            # 4. Cache & Metrics
            self._config = config_obj
            duration_ms = (time.perf_counter() - start_time) * 1000

            self._metrics.publish(Metric(name="lora.config.load_time_ms", value=duration_ms, module="LoRAConfigurationManager"))
            self._metrics.publish(Metric(name="lora.rank", value=config_obj.lora.rank, module="LoRAConfigurationManager"))
            self._metrics.publish(Metric(name="lora.alpha", value=config_obj.lora.alpha, module="LoRAConfigurationManager"))
            self._metrics.publish(Metric(name="lora.dropout", value=config_obj.lora.dropout, module="LoRAConfigurationManager"))
            self._metrics.publish(Metric(name="lora.target_module_count", value=len(config_obj.target_modules.modules), module="LoRAConfigurationManager"))
            self._metrics.publish(Metric(name="lora.training.learning_rate", value=config_obj.training.learning_rate, module="LoRAConfigurationManager"))

            self._logger.info(
                f"LoRA Configuration Loaded. Rank: {config_obj.lora.rank}, "
                f"Alpha: {config_obj.lora.alpha}, "
                f"Target Modules: {len(config_obj.target_modules.modules)}",
                duration_ms=duration_ms
            )

            return self._config

    def to_dict(self) -> Dict[str, Any]:
        """Returns the fully validated configuration as a dictionary."""
        return self.load().model_dump()

    def get_hash_digest(self) -> str:
        """Returns a SHA-256 hash of the current serialized configuration."""
        cfg_dict = self.to_dict()
        cfg_str = json.dumps(cfg_dict, sort_keys=True)
        return hashlib.sha256(cfg_str.encode('utf-8')).hexdigest()

    def export_to_yaml(self, path: str | Path) -> None:
        """Exports the current configuration to a YAML file."""
        cfg_dict = self.to_dict()
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            yaml.dump(cfg_dict, f, default_flow_style=False, sort_keys=False)
        self._logger.info(f"Exported LoRA configuration to YAML at {path}")

    def export_to_json(self, path: str | Path) -> None:
        """Exports the current configuration to a JSON file."""
        cfg_dict = self.to_dict()
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(cfg_dict, f, indent=4)
        self._logger.info(f"Exported LoRA configuration to JSON at {path}")

    def get_pretty_summary(self) -> str:
        """Returns a human-readable summary of the LoRA configuration."""
        config = self.load()
        lines = [
            "=" * 60,
            f"LORA PERSONALIZATION SUMMARY - {config.adapter.name} v{config.adapter.version}",
            "=" * 60,
            f"Hyperparameters:",
            f"  - Rank (r):     {config.lora.rank}",
            f"  - Alpha:        {config.lora.alpha}",
            f"  - Dropout:      {config.lora.dropout}",
            f"  - Bias:         {config.lora.bias}",
            f"  - Task Type:    {config.lora.task_type}",
            f"  - Init Weights: {config.lora.init_lora_weights}",
            f"Target Modules:   {len(config.target_modules.modules)} {config.target_modules.modules}",
            f"Precision:",
            f"  - DType:        {config.precision.dtype}",
            f"  - Mixed Prec:   {config.precision.mixed_precision}",
            f"Training:",
            f"  - Optimizer:    {config.training.optimizer}",
            f"  - LR:           {config.training.learning_rate}",
            f"  - Batch Size:   {config.training.batch_size}",
            f"  - Epochs:       {config.training.epochs}",
            "=" * 60,
            f"Config Hash:      {self.get_hash_digest()}",
            "=" * 60,
        ]
        return "\n".join(lines)
