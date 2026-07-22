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


def get_update_packager(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing UpdatePackager."""
    return container.update_packager()


def get_checksum_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing ChecksumService."""
    return container.checksum_service()


def get_compression_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing CompressionService."""
    return container.compression_service()


def get_encryption_service(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing EncryptionService."""
    return container.encryption_service()


def get_upload_queue(container: ServiceContainer = Depends(get_container)) -> Any:
    """Dependency providing UploadQueue."""
    return container.upload_queue()
