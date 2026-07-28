"""DriftAdapt LoRA Configuration Builder.

Author: DriftAdapt Contributors
Purpose: Transforms API requests into immutable PEFT configurations, standardizing inputs and providing robust validation.
"""

from typing import Optional

from app.schemas.lora_config import LoRAConfigurationRequest
from app.personalization.config.lora_schema import PersonalizationConfiguration
from app.personalization.config.lora_configuration_manager import LoRAConfigurationManager


class ConfigBuilder:
    """Builds and validates LoRA configurations from API schemas."""

    def __init__(self, config_manager: Optional[LoRAConfigurationManager] = None) -> None:
        """Initializes the ConfigBuilder.
        
        Args:
            config_manager: Injected LoRAConfigurationManager. Defaults to global singleton.
        """
        self._config_manager = config_manager or LoRAConfigurationManager()

    def build_configuration(self, request: LoRAConfigurationRequest) -> PersonalizationConfiguration:
        """Translates the API request into a strict PersonalizationConfiguration.
        
        It pulls base defaults from LoRAConfigurationManager and applies the overrides
        specified in the API request, ensuring invariant checks execute automatically via Pydantic.
        
        Args:
            request: The API request schema.
            
        Returns:
            The validated PersonalizationConfiguration.
        """
        overrides = {
            "adapter": {
                "name": request.adapter_name
            },
            "lora": {
                "rank": request.r,
                "alpha": request.lora_alpha,
                "dropout": request.lora_dropout,
                "bias": request.bias,
                "task_type": request.task_type,
                "inference_mode": request.inference_mode
            }
        }
        
        if request.target_modules is not None:
            overrides["target_modules"] = {
                "modules": request.target_modules
            }
            
        # We use a temporary ConfigManager state to parse without mutating global state if needed,
        # but the prompt implies this config runs prior to training.
        # Alternatively, we just construct the Pydantic model directly using defaults
        
        base_config = self._config_manager.load()
        
        # Deep merge would be better, but we can simply construct a new model
        # based on the base_config dictionary and override.
        base_dict = base_config.model_dump()
        
        # Merge adapter
        base_dict["adapter"]["name"] = request.adapter_name
        
        # Merge lora
        base_dict["lora"]["rank"] = request.r
        base_dict["lora"]["alpha"] = request.lora_alpha
        base_dict["lora"]["dropout"] = request.lora_dropout
        base_dict["lora"]["bias"] = request.bias
        base_dict["lora"]["task_type"] = request.task_type
        base_dict["lora"]["inference_mode"] = request.inference_mode
        
        if request.target_modules is not None:
            base_dict["target_modules"]["modules"] = request.target_modules

        # Pydantic validation will happen here
        validated_config = PersonalizationConfiguration(**base_dict)
        return validated_config
