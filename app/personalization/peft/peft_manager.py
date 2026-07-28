"""DriftAdapt PEFT Integration Manager.

Author: DriftAdapt Contributors
Purpose: Singleton facade orchestrating PEFT configuration retrieval, base model loading, adapter injection, validation, and telemetry.
"""

import threading
import time
from typing import Optional

from torch.nn import Module

from app.core.logging import LoggerFactory
from app.core.metrics import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType
from app.core.metrics.exceptions import MetricAlreadyExists

from app.models.foundation.model_manager import ModelManager
from app.personalization.config.lora_configuration_manager import LoRAConfigurationManager

from app.personalization.peft.adapter_factory import AdapterFactory
from app.personalization.peft.injection_engine import InjectionEngine
from app.personalization.peft.adapter_validator import AdapterValidator
from app.personalization.peft.parameter_inspector import ParameterInspector
from app.personalization.peft.adapter_metadata import AdapterMetadata
from app.personalization.peft.peft_loader import PEFTLoader
from app.personalization.peft.peft_exceptions import PEFTIntegrationError

try:
    from peft import PeftModel
except ImportError:
    pass


class PEFTManager:
    """Thread-safe Singleton facade for the PEFT Integration Layer."""

    _instance: Optional["PEFTManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "PEFTManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PEFTManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._logger = LoggerFactory.get_logger("PEFTManager")
            self._metrics = MetricsBus()
            self._register_metrics()
            
            self._model_manager = ModelManager()
            self._config_manager = LoRAConfigurationManager()
            
            self._injection_engine = InjectionEngine()
            self._loader = PEFTLoader()
            
            self._peft_model: Optional["PeftModel"] = None
            self._metadata: Optional[AdapterMetadata] = None
            self._initialized = True

    def _register_metrics(self) -> None:
        metrics = [
            ("lora.adapter.inject.time_ms", MetricType.SYSTEM, "Time taken to inject adapter"),
            ("lora.trainable.parameters", MetricType.SYSTEM, "Number of trainable parameters"),
            ("lora.total.parameters", MetricType.SYSTEM, "Total number of parameters"),
            ("lora.trainable.ratio", MetricType.SYSTEM, "Ratio of trainable to total parameters")
        ]
        for name, mtype, desc in metrics:
            try:
                self._metrics.register_schema(name, mtype, desc)
            except MetricAlreadyExists:
                pass

    def initialize_adapter(self, force_refresh: bool = False) -> "PeftModel":
        """Orchestrates the entire adapter injection lifecycle.
        
        Loads configuration from LoRAConfigurationManager, obtains the frozen base model
        from ModelManager, injects the adapter, validates invariants, publishes metrics, 
        and returns the wrapped model.
        
        Args:
            force_refresh: If True, bypasses cache and forces re-injection.
            
        Returns:
            The peft-wrapped foundation model.
            
        Raises:
            PEFTIntegrationError: For any injection or validation failures.
        """
        if self._peft_model is not None and not force_refresh:
            return self._peft_model

        with self._lock:
            if self._peft_model is not None and not force_refresh:
                return self._peft_model

            self._logger.info("Initializing PEFT adapter workflow...")
            start_time = time.perf_counter()

            # 1. Configuration
            config = self._config_manager.load()
            lora_config = AdapterFactory.create_lora_config(config)

            # 2. Frozen Foundation Model
            base_model = self._model_manager.get_model()
            
            if base_model is None:
                raise PEFTIntegrationError("Foundation model not found in ModelManager.")

            # Pre-injection validation
            AdapterValidator.verify_frozen_base(base_model)
            if config.validation.verify_target_modules:
                AdapterValidator.verify_target_modules_exist(base_model, config.target_modules.modules)

            # 3. Injection
            peft_model = self._injection_engine.inject_lora_adapters(base_model, lora_config)

            # 4. Post-injection Validation
            AdapterValidator.verify_injection(peft_model, config.target_modules.modules)
            
            # 5. Parameter Inspection
            params_info = ParameterInspector.inspect(peft_model)
            if config.validation.verify_parameter_count and params_info["trainable_parameters"] == 0:
                raise PEFTIntegrationError("Zero trainable parameters reported post-injection.")

            # 6. Metadata Tracking
            self._metadata = AdapterMetadata(
                adapter_name=config.adapter.name,
                rank=config.lora.rank,
                alpha=config.lora.alpha,
                target_modules=config.target_modules.modules,
                trainable_parameters=params_info["trainable_parameters"],
                total_parameters=params_info["total_parameters"]
            )
            
            self._peft_model = peft_model
            
            # 7. Metrics & Telemetry
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            self._metrics.publish(Metric(name="lora.adapter.inject.time_ms", value=duration_ms, module="PEFTManager"))
            self._metrics.publish(Metric(name="lora.trainable.parameters", value=self._metadata.trainable_parameters, module="PEFTManager"))
            self._metrics.publish(Metric(name="lora.total.parameters", value=self._metadata.total_parameters, module="PEFTManager"))
            self._metrics.publish(Metric(name="lora.trainable.ratio", value=self._metadata.trainable_ratio, module="PEFTManager"))

            self._logger.info(
                f"PEFT initialization complete. Trainable Params: {self._metadata.trainable_parameters} "
                f"({self._metadata.trainable_ratio:.4%} of {self._metadata.total_parameters} total)"
            )

            return self._peft_model

    def get_model(self) -> "PeftModel":
        """Returns the currently active injected PEFT model.
        
        If not initialized, initializes it first.
        """
        if self._peft_model is None:
            return self.initialize_adapter()
        return self._peft_model
        
    def get_metadata(self) -> AdapterMetadata:
        """Returns metadata about the active adapter injection."""
        if self._metadata is None:
            self.initialize_adapter()
        assert self._metadata is not None
        return self._metadata
