"""DriftAdapt FastAPI Dependencies Module.

Author: DriftAdapt Contributors
Purpose: Provides FastAPI dependency provider functions for injecting ServiceContainer services into endpoints.
Future Integration: Used by all FastAPI route handlers across the platform.
"""

from typing import Any
from fastapi import Depends

from app.container import ServiceContainer
from app.core.config import ConfigManager
from app.core.device import DeviceManager
from app.core.metrics import MetricsBus
from app.core.runtime import RuntimeManager
from app.models.foundation import ModelManager


def get_container() -> ServiceContainer:
    """FastAPI Dependency providing the global ServiceContainer instance."""
    return ServiceContainer()


def get_config_manager(container: ServiceContainer = Depends(get_container)) -> ConfigManager:
    """Dependency providing ConfigManager instance."""
    return container.config_manager()


def get_metrics_bus(container: ServiceContainer = Depends(get_container)) -> MetricsBus:
    """Dependency providing MetricsBus instance."""
    return container.metrics_bus()


def get_device_manager(container: ServiceContainer = Depends(get_container)) -> DeviceManager:
    """Dependency providing DeviceManager instance."""
    return container.device_manager()


def get_runtime_manager(container: ServiceContainer = Depends(get_container)) -> RuntimeManager:
    """Dependency providing RuntimeManager instance."""
    return container.runtime_manager()


def get_model_manager(container: ServiceContainer = Depends(get_container)) -> ModelManager:
    """Dependency providing ModelManager instance."""
    return container.model_manager()


def get_lora_registry(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing LoRA AdapterRegistry."""
    return container.lora_registry()


def get_lora_metadata_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing LoRA MetadataService."""
    return container.lora_metadata_service()

def get_personalization_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing PersonalizationService."""
    return container.personalization_service()


def get_training_metrics_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing TrainingMetricsService."""
    return container.training_metrics_service()


def get_checkpoint_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing CheckpointService."""
    return container.checkpoint_service()
def get_lora_initializer(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing LoRA AdapterInitializer."""
    return container.lora_adapter_initializer()


def get_compression_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing CompressionService."""
    return container.compression_service()


def get_encryption_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing EncryptionService."""
    return container.encryption_service()


def get_aggregation_engine(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing AggregationEngine."""
    return container.aggregation_engine()


def get_aggregation_registry(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing AggregationRegistry."""
    return container.aggregation_registry()


def get_aggregation_history(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing AggregationHistory."""
    return container.aggregation_history()


def get_inference_engine(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing InferenceEngine."""
    return container.inference_engine()


def get_adapter_loader(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing AdapterLoader."""
    return container.inference_adapter_loader()


def get_adapter_registry(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing AdapterRegistry."""
    return container.inference_adapter_registry()


def get_inference_history(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing InferenceHistoryManager."""
    return container.inference_history_manager()


def get_inference_metrics(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing InferenceMetrics."""
    return container.inference_metrics()


def get_validation_engine(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing ValidationEngine."""
    return container.val_validation_engine()


def get_benchmark_engine(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing BenchmarkEngine."""
    return container.val_benchmark_engine()


def get_system_health_monitor(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing SystemHealthMonitor."""
    return container.val_system_health_monitor()


def get_validation_history(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing ValidationHistory."""
    return container.val_history()


def get_validation_report_gen(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing ValidationReportGenerator."""
    return container.val_report_generator()


def get_benchmark_report_gen(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing BenchmarkReportGenerator."""
    return container.val_benchmark_report_generator()


def get_model_integrity_checker(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing ModelIntegrityChecker."""
    return container.val_model_integrity_checker()
