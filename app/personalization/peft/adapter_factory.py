"""DriftAdapt PEFT Adapter Factory.

Author: DriftAdapt Contributors
Purpose: Transforms domain-specific Personalization configurations into Hugging Face peft configuration objects.
"""

from typing import Optional
from app.personalization.config.lora_schema import PersonalizationConfiguration

try:
    from peft import LoraConfig, TaskType
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False


class AdapterFactory:
    """Factory responsible for constructing peft configuration objects."""

    @classmethod
    def create_lora_config(cls, config: PersonalizationConfiguration) -> "LoraConfig":
        """Converts DriftAdapt PersonalizationConfiguration into a peft.LoraConfig.
        
        Args:
            config: Strongly typed personalization configuration from Module 2.1.
            
        Returns:
            peft.LoraConfig ready for injection.
            
        Raises:
            ImportError: If peft is not installed.
        """
        if not PEFT_AVAILABLE:
            raise ImportError("The 'peft' library is required to create a LoraConfig. Please install it.")

        # Map string task type to peft.TaskType enum safely if possible, otherwise use string.
        task_type_str = config.lora.task_type.upper()
        try:
            task_type = TaskType[task_type_str]
        except KeyError:
            task_type = task_type_str

        # Construct LoraConfig mapping hyperparameters
        lora_config = LoraConfig(
            r=config.lora.rank,
            lora_alpha=config.lora.alpha,
            lora_dropout=config.lora.dropout,
            target_modules=config.target_modules.modules,
            bias=config.lora.bias,
            task_type=task_type,
            inference_mode=config.lora.inference_mode,
            fan_in_fan_out=config.lora.fan_in_fan_out,
            modules_to_save=config.lora.modules_to_save if config.lora.modules_to_save else None,
            init_lora_weights=config.lora.init_lora_weights
        )

        return lora_config
