"""DriftAdapt Model Manager Module.

Author: DriftAdapt Contributors
Purpose: Centralized singleton managing foundation model lifecycle: loading, unloading, metrics logging, and status queries.
Future Integration: Communicated with by future LoRA personalization and federated learning engines.
"""

import gc
import threading
import time
from typing import Any, Optional

import torch

from app.core.config import ConfigManager
from app.core.device import DeviceManager
from app.core.logging import LoggerFactory
from app.core.metrics import Metric, MetricsBus, MetricType
from app.models.foundation.interfaces import ModelManagerInterface
from app.models.foundation.model_factory import ModelFactory
from app.models.foundation.model_info import ModelInfo
from app.models.foundation.model_metadata import ModelMetadata
from app.models.foundation.model_utils import (
    estimate_memory_footprint_mb,
    run_sanity_inference,
)
from app.models.foundation.model_validator import ModelValidator

logger = LoggerFactory.get_logger("ModelManager")


class ModelManager(ModelManagerInterface):
    """Singleton orchestrator managing foundation model instances, tokenizers, and metadata."""

    _instance: Optional["ModelManager"] = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "ModelManager":
        """Ensures a single thread-safe global instance exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_manager: Optional[ConfigManager] = None) -> None:
        """Initializes ModelManager properties."""
        if getattr(self, "_initialized", False):
            return

        self._config_manager = config_manager or ConfigManager()
        self._factory = ModelFactory()
        self._model: Any = None
        self._tokenizer: Any = None
        self._metadata: Optional[ModelMetadata] = None
        self._model_info: Optional[ModelInfo] = None
        self._lock = threading.Lock()

        self._initialized = True
        logger.info("ModelManager instance created successfully.")

    def load_model(self, model_name: Optional[str] = None) -> ModelInfo:
        """Loads and prepares the foundation model and tokenizer using ConfigManager parameters.

        Args:
            model_name: Optional target model name override. If None, reads from ConfigManager.

        Returns:
            ModelInfo: Compiled model information report object.
        """
        with self._lock:
            # If already loaded and same model requested, return existing
            config = self._config_manager.get_config()
            target_model = model_name or config.model.foundation_model
            target_tokenizer = config.model.tokenizer

            if self._model is not None and self._metadata is not None and self._metadata.model_name == target_model:
                logger.info(f"Model '{target_model}' is already loaded in memory.")
                return self.get_model_info()

            # Unload any existing model before loading new one
            if self._model is not None:
                self._unload_model_internal()

            start_time = time.time()
            logger.info(f"ModelManager starting load for foundation model: '{target_model}'")

            # Obtain target device from Module 1.4 DeviceManager
            dev_mgr = DeviceManager()
            device = dev_mgr.resolve_device(config.system.device)

            # Create model & tokenizer via factory
            model, tokenizer, metadata = self._factory.create_model_and_tokenizer(
                model_name=target_model,
                tokenizer_name=target_tokenizer,
                quantization=config.model.quantization,
                precision=config.model.precision,
                device=device,
                cache_dir=config.model.cache_dir,
            )

            # Validate frozen state and tokenizer compatibility
            ModelValidator.validate_tokenizer_compatibility(model, tokenizer)
            ModelValidator.validate_frozen_state(model)

            self._model = model
            self._tokenizer = tokenizer
            self._metadata = metadata
            self._model_info = ModelInfo(metadata)

            elapsed_ms = (time.time() - start_time) * 1000

            # Publish initialization metrics through MetricsBus
            self._publish_metrics(elapsed_ms)

            logger.info(f"ModelManager successfully loaded model '{target_model}'.")
            return self._model_info

    def unload_model(self) -> None:
        """Unloads current model weights from memory and runs garbage collection."""
        with self._lock:
            self._unload_model_internal()

    def _unload_model_internal(self) -> None:
        """Internal helper to free model references and clear CUDA cache."""
        if self._model is not None:
            model_name = self._metadata.model_name if self._metadata else "unknown"
            logger.info(f"Unloading model '{model_name}' from memory...")
            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None
            self._metadata = None
            self._model_info = None

            # Force garbage collection and CUDA cache release
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"Model '{model_name}' unloaded cleanly.")

    def reload_model(self) -> ModelInfo:
        """Unloads current model and reloads it fresh from configuration."""
        self.unload_model()
        return self.load_model()

    def get_model(self) -> Any:
        """Returns the loaded PyTorch model instance."""
        if self._model is None:
            self.load_model()
        return self._model

    def get_tokenizer(self) -> Any:
        """Returns the loaded tokenizer instance."""
        if self._tokenizer is None:
            self.load_model()
        return self._tokenizer

    def get_metadata(self) -> ModelMetadata:
        """Returns ModelMetadata for the currently loaded model."""
        if self._metadata is None:
            self.load_model()
        assert self._metadata is not None
        return self._metadata

    def get_model_info(self) -> ModelInfo:
        """Returns ModelInfo report wrapper for the loaded model."""
        if self._model_info is None:
            self.load_model()
        assert self._model_info is not None
        return self._model_info

    def get_memory_usage(self) -> float:
        """Returns current model memory footprint in Megabytes (MB)."""
        if self._model is None:
            return 0.0
        return estimate_memory_footprint_mb(self._model)

    def validate_sanity_inference(self, prompt: str = "Hello") -> str:
        """Runs a lightweight non-trainable generation inference test on the loaded model."""
        model = self.get_model()
        tokenizer = self.get_tokenizer()
        meta = self.get_metadata()

        return run_sanity_inference(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            max_new_tokens=10,
            device=meta.device,
        )

    def _publish_metrics(self, load_time_ms: float) -> None:
        """Publishes model loading and memory telemetry metrics to MetricsBus."""
        try:
            bus = MetricsBus()
            meta = self._metadata
            if meta is None:
                return

            metrics_to_publish = [
                ("model.load_time_ms", load_time_ms, MetricType.SYSTEM),
                ("model.memory_footprint_mb", meta.memory_footprint_mb, MetricType.MEMORY),
                ("model.parameter_count", meta.parameter_count, MetricType.SYSTEM),
            ]

            for name, val, cat in metrics_to_publish:
                if not bus._registry.is_registered(name):
                    bus.register_schema(name, cat, f"Model metric: {name}")

                bus.publish(
                    Metric(
                        name=name,
                        value=float(val),
                        module="ModelManager",
                    )
                )
        except Exception as e:
            logger.warning(f"Failed to publish model metrics to MetricsBus: {e}")
