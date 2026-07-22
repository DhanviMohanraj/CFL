"""DriftAdapt Foundation Model Exceptions Module.

Author: DriftAdapt Contributors
Purpose: Defines custom exceptions for model loading, tokenizers, quantization, and registry.
Future Integration: Raised by ModelLoader, TokenizerLoader, and ModelManager.
"""


class FoundationModelError(Exception):
    """Base exception for all foundation model errors in DriftAdapt."""

    pass


class ModelLoadError(FoundationModelError):
    """Raised when loading foundation model weights fails."""

    pass


class TokenizerLoadError(FoundationModelError):
    """Raised when loading or configuring the tokenizer fails."""

    pass


class ModelValidationError(FoundationModelError):
    """Raised when model integrity, files, or compatibility checks fail."""

    pass


class QuantizationError(FoundationModelError):
    """Raised when quantization configuration or bitsandbytes setup fails."""

    pass


class CacheError(FoundationModelError):
    """Raised when model cache operations or path resolutions fail."""

    pass


class DownloadError(FoundationModelError):
    """Raised when downloading model weights from remote repositories fails."""

    pass


class UnsupportedModelError(FoundationModelError):
    """Raised when a requested model architecture or repository is not supported in the registry."""

    pass
