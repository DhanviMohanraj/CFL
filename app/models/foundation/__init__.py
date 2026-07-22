"""DriftAdapt Foundation Models Package.

Author: DriftAdapt Contributors
Purpose: Exposes ModelManager, ModelFactory, ModelLoader, TokenizerLoader, ModelRegistry, and metadata schemas.
Future Integration: Referenced by Module 2 (LoRA Personalization) and downstream components.
"""

from app.models.foundation.cache_manager import CacheManager
from app.models.foundation.download_manager import DownloadManager
from app.models.foundation.exceptions import (
    CacheError,
    DownloadError,
    FoundationModelError,
    ModelLoadError,
    ModelValidationError,
    QuantizationError,
    TokenizerLoadError,
    UnsupportedModelError,
)
from app.models.foundation.interfaces import (
    ModelLoaderInterface,
    ModelManagerInterface,
    TokenizerLoaderInterface,
)
from app.models.foundation.model_factory import ModelFactory
from app.models.foundation.model_info import ModelInfo
from app.models.foundation.model_loader import ModelLoader
from app.models.foundation.model_manager import ModelManager
from app.models.foundation.model_metadata import ModelMetadata
from app.models.foundation.model_registry import ModelRegistry, ModelSpec
from app.models.foundation.model_utils import (
    count_parameters,
    estimate_memory_footprint_mb,
    freeze_all_parameters,
    run_sanity_inference,
    verify_frozen_parameters,
)
from app.models.foundation.model_validator import ModelValidator
from app.models.foundation.quantization import QuantizationManager
from app.models.foundation.tokenizer_loader import TokenizerLoader

__all__ = [
    "FoundationModelError",
    "ModelLoadError",
    "TokenizerLoadError",
    "ModelValidationError",
    "QuantizationError",
    "CacheError",
    "DownloadError",
    "UnsupportedModelError",
    "ModelLoaderInterface",
    "TokenizerLoaderInterface",
    "ModelManagerInterface",
    "ModelMetadata",
    "ModelInfo",
    "ModelRegistry",
    "ModelSpec",
    "count_parameters",
    "freeze_all_parameters",
    "verify_frozen_parameters",
    "estimate_memory_footprint_mb",
    "run_sanity_inference",
    "QuantizationManager",
    "CacheManager",
    "DownloadManager",
    "ModelValidator",
    "TokenizerLoader",
    "ModelLoader",
    "ModelFactory",
    "ModelManager",
]
