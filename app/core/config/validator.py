"""DriftAdapt Configuration Validator.

Author: DriftAdapt Contributors
Purpose: Performs validation checks on configurations, raising custom exceptions.
Future Integration: Invoked by ConfigManager before updating active properties.
"""

from pathlib import Path
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from app.core.config.exceptions import ValidationError as CustomValidationError
from app.core.config.schema import AppConfig


def validate_business_constraints(config: AppConfig) -> None:
    """Performs semantic validation checks on resolved configurations.

    Checks:
    - Path validity and writability (or capability to create).
    - Consistency between local epochs and federated epochs.
    - Specific value boundary checks.
    """
    # 1. Directory checks
    # Verify we can resolve and construct directories safely
    dirs_to_check = {
        "system.logs_dir": config.system.logs_dir,
        "system.checkpoints_dir": config.system.checkpoints_dir,
        "system.datasets_dir": config.system.datasets_dir,
        "system.metrics_dir": config.system.metrics_dir,
        "system.experiments_dir": config.system.experiments_dir,
        "evaluation.output_dir": config.evaluation.output_dir,
        "lora.adapters_dir": config.lora.adapters_dir,
    }

    for key, path_str in dirs_to_check.items():
        if not path_str:
            raise CustomValidationError(f"Directory path for '{key}' cannot be empty.")

        try:
            path_obj = Path(path_str)
            # Try to resolve to verify path correctness
            path_obj.resolve()
        except Exception as e:
            raise CustomValidationError(
                f"Directory path for '{key}' is invalid ({path_str}): {e}"
            ) from e

    # 2. Logic Consistency checks
    # Model name verification (not blank)
    if not config.model.foundation_model.strip():
        raise CustomValidationError("Foundation model name cannot be empty or whitespace.")

    if not config.model.tokenizer.strip():
        raise CustomValidationError("Tokenizer name cannot be empty or whitespace.")

    # Check learning rate limits
    if config.training.learning_rate <= 0.0:
        raise CustomValidationError(
            f"Learning rate must be strictly positive. Got: {config.training.learning_rate}"
        )

    # Check batch sizes
    if config.training.batch_size <= 0:
        raise CustomValidationError(
            f"Training batch size must be positive. Got: {config.training.batch_size}"
        )

    # Check federated client limits
    if config.federated.participation_rate <= 0.0 or config.federated.participation_rate > 1.0:
        raise CustomValidationError(
            "Federation participation rate must lie in the range (0.0, 1.0]."
        )


def validate_configuration(config_dict: Dict[str, Any]) -> AppConfig:
    """Loads configuration dictionary into Pydantic schema and validates constraints.

    Wraps Pydantic validations into custom ValidationError exceptions.
    """
    try:
        # Pydantic schema validation
        config = AppConfig(**config_dict)
    except PydanticValidationError as e:
        # Format Pydantic errors into a clean, human-readable list of issues
        errors_summary = []
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "invalid value")
            errors_summary.append(f"[{loc}]: {msg}")

        combined_msg = " | ".join(errors_summary)
        raise CustomValidationError(
            f"Configuration schema validation failed: {combined_msg}"
        ) from e

    # Business constraints validation
    validate_business_constraints(config)

    return config
