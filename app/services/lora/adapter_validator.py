"""DriftAdapt API Adapter Validator Service.

Author: DriftAdapt Contributors
Purpose: Exposes a higher-level validation service for API endpoints that translates underlying PEFT errors into structured responses.
"""

from typing import Tuple, List
from torch.nn import Module

from app.core.logging import LoggerFactory
from app.personalization.peft.adapter_validator import AdapterValidator
from app.personalization.peft.peft_exceptions import PEFTIntegrationError


class AdapterValidatorService:
    """Service to validate adapter configurations prior to API injection."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("AdapterValidatorService")

    def validate_pre_injection(self, base_model: Module, target_modules: List[str]) -> Tuple[bool, List[str]]:
        """Validates if the base model and configuration are compatible.
        
        Args:
            base_model: The frozen PyTorch model.
            target_modules: The proposed target modules.
            
        Returns:
            A tuple of (is_valid, list_of_warnings_or_errors).
        """
        warnings = []
        is_valid = True
        
        self._logger.info("Running pre-injection validation...")

        try:
            AdapterValidator.verify_frozen_base(base_model)
        except PEFTIntegrationError as e:
            is_valid = False
            warnings.append(str(e))
            self._logger.warning(f"Pre-injection frozen check failed: {e}")

        try:
            AdapterValidator.verify_target_modules_exist(base_model, target_modules)
        except PEFTIntegrationError as e:
            is_valid = False
            warnings.append(str(e))
            self._logger.warning(f"Pre-injection target module check failed: {e}")

        return is_valid, warnings

    def validate_post_injection(self, injected_model: Module, target_modules: List[str]) -> Tuple[bool, List[str]]:
        """Validates if the injected model meets structural safety guarantees.
        
        Args:
            injected_model: The PEFT-wrapped model.
            target_modules: The configured target modules.
            
        Returns:
            A tuple of (is_valid, list_of_warnings_or_errors).
        """
        warnings = []
        is_valid = True
        
        self._logger.info("Running post-injection validation...")

        try:
            AdapterValidator.verify_injection(injected_model, target_modules)
        except PEFTIntegrationError as e:
            is_valid = False
            warnings.append(str(e))
            self._logger.warning(f"Post-injection safety check failed: {e}")

        return is_valid, warnings
