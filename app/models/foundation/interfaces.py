"""DriftAdapt Foundation Model Interfaces Module.

Author: DriftAdapt Contributors
Purpose: Defines abstract base classes for model loaders, tokenizer loaders, and model managers.
Future Integration: Enforced across all foundation model implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ModelLoaderInterface(ABC):
    """Abstract interface for loading and preparing foundation language models."""

    @abstractmethod
    def load_model(
        self,
        model_name_or_path: str,
        device: Any,
        quantization: Optional[str] = None,
        precision: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ) -> Any:
        """Loads and returns the foundation language model."""
        pass


class TokenizerLoaderInterface(ABC):
    """Abstract interface for loading and configuring model tokenizers."""

    @abstractmethod
    def load_tokenizer(
        self,
        tokenizer_name_or_path: str,
        cache_dir: Optional[str] = None,
        use_fast: bool = True,
    ) -> Any:
        """Loads and returns the tokenizer."""
        pass


class ModelManagerInterface(ABC):
    """Abstract interface for managing model lifecycles."""

    @abstractmethod
    def load_model(self, model_name: Optional[str] = None) -> Any:
        """Loads and prepares the model and tokenizer."""
        pass

    @abstractmethod
    def unload_model(self) -> None:
        """Unloads model weights from memory and frees resources."""
        pass

    @abstractmethod
    def get_model(self) -> Any:
        """Returns the currently loaded PyTorch model."""
        pass

    @abstractmethod
    def get_tokenizer(self) -> Any:
        """Returns the currently loaded tokenizer."""
        pass
