"""Validation Engine Service.

Author: DriftAdapt Contributors
Purpose: Coordinates integrity and pipeline validators to confirm system readiness.
"""

import time

from app.core.logging import LoggerFactory
from app.schemas.validation_request import ValidationRequest
from app.schemas.validation_result import ValidationResult
from app.services.validation.model_integrity_checker import ModelIntegrityChecker
from app.services.validation.adapter_validator import AdapterValidator
from app.services.validation.inference_validator import InferenceValidator
from app.services.validation.metrics_collector import MetricsCollector
from app.services.validation.validation_history import ValidationHistory
from app.services.validation.validation_registry import ValidationRegistry


class ValidationEngine:
    """The master QA orchestrator."""
    
    def __init__(
        self,
        integrity_checker: ModelIntegrityChecker,
        adapter_validator: AdapterValidator,
        inference_validator: InferenceValidator,
        metrics_collector: MetricsCollector,
        history: ValidationHistory,
        registry: ValidationRegistry
    ) -> None:
        self._logger = LoggerFactory.get_logger("ValidationEngine")
        self._integrity = integrity_checker
        self._adapter_val = adapter_validator
        self._inference_val = inference_validator
        self._metrics = metrics_collector
        self._history = history
        self._registry = registry

    def run_validation(self, request: ValidationRequest) -> ValidationResult:
        """Executes a full or partial validation sweep."""
        if self._registry.is_validation_running():
            raise RuntimeError("Another validation sweep is currently running.")
            
        self._registry.register_validation(request.validation_id)
        start_time = time.perf_counter()
        
        warnings = []
        errors = []
        
        model_stat = "NOT_CHECKED"
        adapter_stat = "NOT_CHECKED"
        inf_stat = "NOT_CHECKED"
        int_stat = "NOT_CHECKED"
        
        try:
            self._logger.info(f"Starting validation sweep {request.validation_id}")
            
            # 1. Model Integrity
            if "model" in request.validation_scope:
                ok, report = self._integrity.check_integrity()
                if ok:
                    model_stat = "PASSED"
                    int_stat = "PASSED"
                else:
                    model_stat = "FAILED"
                    int_stat = "FAILED"
                    errors.append("Model integrity check failed.")
                    
            # 2. Adapter
            if "adapter" in request.validation_scope and request.adapter_id:
                ok, msg = self._adapter_val.validate_loaded_adapter(request.adapter_id)
                if ok:
                    adapter_stat = "PASSED"
                else:
                    adapter_stat = "FAILED"
                    errors.append(f"Adapter validation failed: {msg}")
                    
            # 3. Inference Pipeline
            if "inference" in request.validation_scope:
                # Need model and adapter checks to pass or be skipped
                if "FAILED" not in [model_stat, adapter_stat]:
                    ok, msg = self._inference_val.validate_inference_pipeline()
                    if ok:
                        inf_stat = "PASSED"
                    else:
                        inf_stat = "FAILED"
                        errors.append(f"Inference pipeline failure: {msg}")
                else:
                    inf_stat = "SKIPPED"
                    warnings.append("Skipped inference validation due to prior failure.")
                    
            elapsed = time.perf_counter() - start_time
            success = len(errors) == 0
            
            result = ValidationResult(
                success=success,
                validation_id=request.validation_id,
                validation_status="COMPLETED" if success else "FAILED",
                adapter_status=adapter_stat,
                model_status=model_stat,
                inference_status=inf_stat,
                integrity_status=int_stat,
                execution_time=elapsed,
                warnings=warnings,
                errors=errors
            )
            
            self._history.record_validation(result)
            self._metrics.collect_validation_metrics(result)
            
            self._logger.info(f"Completed validation sweep {request.validation_id}. Success: {success}")
            return result
            
        except Exception as e:
            self._logger.error(f"Validation sweep {request.validation_id} crashed.", error=str(e))
            elapsed = time.perf_counter() - start_time
            
            result = ValidationResult(
                success=False,
                validation_id=request.validation_id,
                validation_status="CRASHED",
                execution_time=elapsed,
                errors=[str(e)]
            )
            self._history.record_validation(result)
            self._metrics.collect_validation_metrics(result)
            return result
            
        finally:
            self._registry.unregister_validation(request.validation_id)
