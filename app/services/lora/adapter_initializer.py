"""DriftAdapt LoRA Adapter Initializer.

Author: DriftAdapt Contributors
Purpose: Exposes the core service logic bridging the API configuration layer with the internal PEFT module.
"""

import time
import uuid
from typing import Optional
from datetime import datetime

from app.core.logging import LoggerFactory
from app.models.foundation.model_manager import ModelManager

from app.schemas.lora_config import LoRAConfigurationRequest
from app.schemas.adapter_metadata import AdapterMetadataResponse
from app.schemas.initialization_result import InitializationResultResponse

from app.services.lora.config_builder import ConfigBuilder
from app.services.lora.target_module_selector import TargetModuleSelector
from app.services.lora.adapter_validator import AdapterValidatorService
from app.services.lora.adapter_registry import AdapterRegistry

from app.personalization.peft.adapter_factory import AdapterFactory
from app.personalization.peft.injection_engine import InjectionEngine
from app.personalization.peft.parameter_inspector import ParameterInspector


class AdapterInitializer:
    """Service coordinating the initialization of new LoRA adapters."""

    def __init__(
        self,
        model_manager: ModelManager,
        registry: AdapterRegistry,
        config_builder: Optional[ConfigBuilder] = None,
        module_selector: Optional[TargetModuleSelector] = None,
        validator: Optional[AdapterValidatorService] = None
    ) -> None:
        self._logger = LoggerFactory.get_logger("AdapterInitializer")
        self._model_manager = model_manager
        self._registry = registry
        
        self._config_builder = config_builder or ConfigBuilder()
        self._module_selector = module_selector or TargetModuleSelector()
        self._validator = validator or AdapterValidatorService()
        self._injection_engine = InjectionEngine()

    def initialize_adapter(self, request: LoRAConfigurationRequest) -> InitializationResultResponse:
        """Initializes a PEFT adapter based on the incoming API request.
        
        Args:
            request: The API configuration schema.
            
        Returns:
            InitializationResultResponse containing status and timing.
        """
        start_time = time.perf_counter()
        warnings = []
        
        base_model = self._model_manager.get_model()
        if base_model is None:
            return InitializationResultResponse(
                success=False,
                adapter_loaded=False,
                validation_status="FAILED: No foundation model loaded",
                configuration_summary={},
                warnings=["Foundation model not available in ModelManager."],
                initialization_time_ms=(time.perf_counter() - start_time) * 1000,
                adapter_id=None
            )

        # 1. Target Modules Auto-Discovery
        target_modules = request.target_modules
        if not target_modules:
            target_modules = self._module_selector.discover_modules(base_model)
            request.target_modules = target_modules
            warnings.append(f"Auto-discovered target modules: {target_modules}")

        # 2. Build Internal Configuration
        try:
            internal_config = self._config_builder.build_configuration(request)
        except Exception as e:
            return InitializationResultResponse(
                success=False,
                adapter_loaded=False,
                validation_status="FAILED: Config Build",
                configuration_summary={},
                warnings=[str(e)],
                initialization_time_ms=(time.perf_counter() - start_time) * 1000,
                adapter_id=None
            )

        # 3. Pre-Injection Validation
        is_valid, pre_warnings = self._validator.validate_pre_injection(base_model, internal_config.target_modules.modules)
        warnings.extend(pre_warnings)
        if not is_valid:
            return InitializationResultResponse(
                success=False,
                adapter_loaded=False,
                validation_status="FAILED: Pre-injection checks",
                configuration_summary=internal_config.model_dump(),
                warnings=warnings,
                initialization_time_ms=(time.perf_counter() - start_time) * 1000,
                adapter_id=None
            )

        # 4. Inject Adapters
        lora_config = AdapterFactory.create_lora_config(internal_config)
        try:
            peft_model = self._injection_engine.inject_lora_adapters(base_model, lora_config)
        except Exception as e:
            return InitializationResultResponse(
                success=False,
                adapter_loaded=False,
                validation_status="FAILED: Injection Engine Error",
                configuration_summary=internal_config.model_dump(),
                warnings=warnings + [str(e)],
                initialization_time_ms=(time.perf_counter() - start_time) * 1000,
                adapter_id=None
            )

        # 5. Post-Injection Validation
        is_valid_post, post_warnings = self._validator.validate_post_injection(peft_model, internal_config.target_modules.modules)
        warnings.extend(post_warnings)
        if not is_valid_post:
            return InitializationResultResponse(
                success=False,
                adapter_loaded=True,
                validation_status="FAILED: Post-injection checks",
                configuration_summary=internal_config.model_dump(),
                warnings=warnings,
                initialization_time_ms=(time.perf_counter() - start_time) * 1000,
                adapter_id=None
            )

        # 6. Parameter Inspection
        params_info = ParameterInspector.inspect(peft_model)
        
        # 7. Register Metadata
        adapter_id = str(uuid.uuid4())
        model_name = "unknown"
        metadata_obj = self._model_manager.get_metadata()
        if metadata_obj:
            model_name = metadata_obj.model_name
            
        metadata = AdapterMetadataResponse(
            adapter_id=adapter_id,
            adapter_name=request.adapter_name,
            creation_timestamp=datetime.utcnow().isoformat(),
            model_name=model_name,
            parameter_count=params_info["total_parameters"],
            trainable_parameters=params_info["trainable_parameters"],
            frozen_parameters=params_info["total_parameters"] - params_info["trainable_parameters"],
            adapter_rank=request.r,
            adapter_alpha=request.lora_alpha,
            adapter_dropout=request.lora_dropout,
            adapter_version="1.0",
            target_modules=internal_config.target_modules.modules
        )
        
        self._registry.register(metadata)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        return InitializationResultResponse(
            success=True,
            adapter_loaded=True,
            validation_status="PASSED",
            configuration_summary=internal_config.model_dump(),
            warnings=warnings,
            initialization_time_ms=duration_ms,
            adapter_id=adapter_id
        )
