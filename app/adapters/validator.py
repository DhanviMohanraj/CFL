"""DriftAdapt Adapter State Validator.

Author: DriftAdapt Contributors
Purpose: Performs structural validations on adapter state dictionaries.
"""

from typing import Any, Dict, Optional

try:
    import torch
except ImportError:
    torch = None

from app.adapters.exceptions import ValidationFailed
from app.adapters.metrics import AdapterMetricsPublisher
from app.adapters.schemas import ValidationReport
from app.core.logging.logger_factory import LoggerFactory


class AdapterStateValidator:
    """Validates structural properties of adapter states."""

    def __init__(self, strict: bool = True) -> None:
        """Initializes the validator.
        
        Args:
            strict: If True, raises ValidationFailed on errors.
        """
        self._strict = strict
        self._logger = LoggerFactory.get_logger("AdapterStateValidator")
        self._metrics = AdapterMetricsPublisher()

    def validate(
        self, state_dict: Dict[str, Any], reference_state: Optional[Dict[str, Any]] = None
    ) -> ValidationReport:
        """Runs a complete validation suite on the state_dict.
        
        Args:
            state_dict: The state dictionary to validate.
            reference_state: Optional expected baseline state for shape/key cross-checking.
            
        Returns:
            ValidationReport detailing the outcome.
            
        Raises:
            ValidationFailed: If strict mode is enabled and errors are found.
        """
        report = ValidationReport(success=True)
        report.parameter_count = len(state_dict)

        if len(state_dict) == 0:
            report.success = False
            report.errors.append("Adapter state is empty.")
            
        self.validate_keys(state_dict, report)
        self.validate_dtype(state_dict, report)
        
        if reference_state is not None:
            self.validate_compatibility(state_dict, reference_state, report)

        if not report.success and self._strict:
            self._metrics.publish("validation_failure", 1)
            self._logger.error(f"Strict validation failed with errors: {report.errors}")
            raise ValidationFailed(f"Validation failed: {report.errors}")
            
        if report.success:
            self._metrics.publish("validation_success", 1)

        return report

    def validate_keys(self, state_dict: Dict[str, Any], report: ValidationReport) -> None:
        """Validates that keys follow expected LoRA conventions."""
        for key in state_dict.keys():
            if "lora_" not in key:
                report.warnings.append(f"Suspicious key without 'lora_' pattern: {key}")

    def validate_dtype(self, state_dict: Dict[str, Any], report: ValidationReport) -> None:
        """Validates that values are torch Tensors if torch is available."""
        if torch is None:
            return
        
        for key, value in state_dict.items():
            if not isinstance(value, torch.Tensor):
                report.success = False
                report.errors.append(f"Value for {key} is not a torch.Tensor, got {type(value)}.")

    def validate_shapes(
        self, state_dict: Dict[str, Any], reference_state: Dict[str, Any], report: ValidationReport
    ) -> None:
        """Validates tensor shapes against a reference state."""
        for key, value in state_dict.items():
            if key in reference_state:
                ref_val = reference_state[key]
                if hasattr(value, "shape") and hasattr(ref_val, "shape"):
                    if value.shape != ref_val.shape:
                        report.success = False
                        report.shape_mismatches.append(key)
                        report.errors.append(f"Shape mismatch for {key}: {value.shape} != {ref_val.shape}")

    def validate_compatibility(
        self, state_dict: Dict[str, Any], reference_state: Dict[str, Any], report: ValidationReport
    ) -> None:
        """Cross-checks missing or unexpected parameters."""
        state_keys = set(state_dict.keys())
        ref_keys = set(reference_state.keys())
        
        missing = list(ref_keys - state_keys)
        unexpected = list(state_keys - ref_keys)
        
        if missing:
            report.success = False
            report.missing_parameters = missing
            report.errors.append(f"Missing {len(missing)} expected parameters.")
            
        if unexpected:
            report.success = False
            report.unexpected_parameters = unexpected
            report.errors.append(f"Found {len(unexpected)} unexpected parameters.")

        self.validate_shapes(state_dict, reference_state, report)
