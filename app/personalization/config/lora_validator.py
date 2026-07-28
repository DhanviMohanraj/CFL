"""DriftAdapt Personalization LoRA Configuration Validator.

Author: DriftAdapt Contributors
Purpose: Performs deep, domain-specific validation of LoRA configuration dictionaries prior to Pydantic instantiation.
"""

from typing import Dict, Any, List

from app.personalization.config.lora_exceptions import (
    InvalidRankError,
    InvalidAlphaError,
    InvalidDropoutError,
    InvalidTargetModuleError,
    InvalidTrainingParameterError,
    InvalidCheckpointConfigurationError,
    InvalidPrecisionError,
    InvalidTaskTypeError,
    InvalidStorageConfigurationError,
)

SUPPORTED_TASK_TYPES = {"CAUSAL_LM", "SEQ_2_SEQ_LM", "TOKEN_CLS", "SEQ_CLS"}
SUPPORTED_PRECISIONS = {"float32", "float16", "bfloat16"}


class LoRAConfigurationValidator:
    """Validates raw configuration dictionaries for LoRA logic constraints."""

    @classmethod
    def validate(cls, raw_config: Dict[str, Any]) -> None:
        """Executes all validation checks on the raw dictionary.

        Args:
            raw_config: The deeply merged configuration dictionary.
            
        Raises:
            Various LoRAConfigurationError subclasses if validation fails.
        """
        # We assume structure is somewhat guaranteed by defaults, but we use .get with defaults where safe
        # However, since this runs before Pydantic, we need to be careful with types.
        
        cls._validate_lora_hyperparameters(raw_config.get("lora", {}))
        cls._validate_target_modules(raw_config.get("target_modules", {}))
        cls._validate_training_parameters(raw_config.get("training", {}))
        cls._validate_checkpoint_parameters(raw_config.get("checkpoint", {}))
        cls._validate_precision_parameters(raw_config.get("precision", {}))
        cls._validate_storage_parameters(raw_config.get("storage", {}))

    @classmethod
    def _validate_lora_hyperparameters(cls, lora_cfg: Dict[str, Any]) -> None:
        rank = lora_cfg.get("rank", 16)
        if not isinstance(rank, int) or rank <= 0:
            raise InvalidRankError(f"LoRA rank must be a positive integer, got {rank}")

        alpha = lora_cfg.get("alpha", 32.0)
        if not isinstance(alpha, (int, float)) or alpha <= 0:
            raise InvalidAlphaError(f"LoRA alpha must be a positive number, got {alpha}")

        dropout = lora_cfg.get("dropout", 0.05)
        if not isinstance(dropout, (int, float)) or not (0.0 <= dropout <= 1.0):
            raise InvalidDropoutError(f"LoRA dropout must be between 0.0 and 1.0, got {dropout}")

        task_type = lora_cfg.get("task_type", "CAUSAL_LM")
        if task_type not in SUPPORTED_TASK_TYPES:
            raise InvalidTaskTypeError(f"Unsupported PEFT task type '{task_type}'. Must be one of {SUPPORTED_TASK_TYPES}")

    @classmethod
    def _validate_target_modules(cls, tm_cfg: Dict[str, Any]) -> None:
        modules: List[str] = tm_cfg.get("modules", [])
        if not modules:
            raise InvalidTargetModuleError("Target modules list cannot be empty.")
        
        if len(modules) != len(set(modules)):
            raise InvalidTargetModuleError("Target modules list contains duplicate entries.")

    @classmethod
    def _validate_training_parameters(cls, train_cfg: Dict[str, Any]) -> None:
        lr = train_cfg.get("learning_rate", 2e-4)
        if not isinstance(lr, (int, float)) or lr <= 0:
            raise InvalidTrainingParameterError(f"Learning rate must be positive, got {lr}")

        bs = train_cfg.get("batch_size", 4)
        if not isinstance(bs, int) or bs <= 0:
            raise InvalidTrainingParameterError(f"Batch size must be a positive integer, got {bs}")

        epochs = train_cfg.get("epochs", 3)
        if not isinstance(epochs, int) or epochs <= 0:
            raise InvalidTrainingParameterError(f"Epochs must be a positive integer, got {epochs}")

        gas = train_cfg.get("gradient_accumulation_steps", 4)
        if not isinstance(gas, int) or gas <= 0:
            raise InvalidTrainingParameterError(f"Gradient accumulation steps must be positive, got {gas}")

        wd = train_cfg.get("weight_decay", 0.001)
        if not isinstance(wd, (int, float)) or wd < 0:
            raise InvalidTrainingParameterError(f"Weight decay must be non-negative, got {wd}")

        warmup = train_cfg.get("warmup_ratio", 0.03)
        if not isinstance(warmup, (int, float)) or not (0.0 <= warmup <= 1.0):
            raise InvalidTrainingParameterError(f"Warmup ratio must be between 0.0 and 1.0, got {warmup}")

    @classmethod
    def _validate_checkpoint_parameters(cls, ckpt_cfg: Dict[str, Any]) -> None:
        save_every = ckpt_cfg.get("save_every", 100)
        if not isinstance(save_every, int) or save_every <= 0:
            raise InvalidCheckpointConfigurationError(f"save_every must be a positive integer, got {save_every}")
            
        keep_last = ckpt_cfg.get("keep_last", 3)
        if not isinstance(keep_last, int) or keep_last < 0:
            raise InvalidCheckpointConfigurationError(f"keep_last must be non-negative, got {keep_last}")

    @classmethod
    def _validate_precision_parameters(cls, prec_cfg: Dict[str, Any]) -> None:
        dtype = prec_cfg.get("dtype", "bfloat16")
        if dtype not in SUPPORTED_PRECISIONS:
            raise InvalidPrecisionError(f"Precision dtype '{dtype}' is not supported. Must be one of {SUPPORTED_PRECISIONS}")

    @classmethod
    def _validate_storage_parameters(cls, storage_cfg: Dict[str, Any]) -> None:
        for key in ["adapter_directory", "checkpoint_directory", "export_directory", "temporary_directory", "cache_directory"]:
            val = storage_cfg.get(key, "")
            if not isinstance(val, str) or not val.strip():
                raise InvalidStorageConfigurationError(f"Storage path for '{key}' cannot be empty.")
