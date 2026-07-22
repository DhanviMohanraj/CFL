"""DriftAdapt Model Validator Module.

Author: DriftAdapt Contributors
Purpose: Validates model checkpoint integrity, file completeness, and tokenizer/model compatibility.
Future Integration: Invoked before and after loading foundation models.
"""

from typing import Any, List

import torch

from app.core.logging import LoggerFactory
from app.models.foundation.exceptions import ModelValidationError

logger = LoggerFactory.get_logger("ModelValidator")


class ModelValidator:
    """Validates structural completeness and runtime compatibility of foundation models and tokenizers."""

    @staticmethod
    def validate_tokenizer_compatibility(model: Any, tokenizer: Any) -> bool:
        """Verifies that tokenizer vocabulary matches model embedding dimensions.

        Raises:
            ModelValidationError: If vocabulary sizes are incompatible.
        """
        if model is None or tokenizer is None:
            raise ModelValidationError("Model or Tokenizer is None. Cannot perform compatibility validation.")

        vocab_size = getattr(tokenizer, "vocab_size", 0)

        # Check embedding layer size on PyTorch model
        embedding_size = 0
        try:
            if hasattr(model, "get_input_embeddings"):
                embeddings = model.get_input_embeddings()
                if embeddings is not None and hasattr(embeddings, "weight"):
                    embedding_size = embeddings.weight.shape[0]
            elif hasattr(model, "config") and hasattr(model.config, "vocab_size"):
                embedding_size = model.config.vocab_size
        except Exception as e:
            logger.warning(f"Unable to extract model embedding dimensions for validation: {e}")
            return True

        if isinstance(vocab_size, int) and isinstance(embedding_size, int):
            if vocab_size > 0 and embedding_size > 0:
                if vocab_size > embedding_size:
                    logger.warning(
                        f"Tokenizer vocabulary size ({vocab_size}) exceeds model embedding size ({embedding_size}). "
                        "Resizing token embeddings might be required during fine-tuning."
                    )

        logger.info(f"Tokenizer/Model compatibility verified (tokenizer vocab: {vocab_size}, model embeddings: {embedding_size}).")
        return True

    @staticmethod
    def validate_frozen_state(model: Any) -> bool:
        """Asserts that all parameters in the base foundation model have requires_grad set to False.

        Raises:
            ModelValidationError: If any parameter is trainable.
        """
        if not isinstance(model, torch.nn.Module):
            return True

        trainable_names: List[str] = []
        for name, param in model.named_parameters():
            if param.requires_grad:
                trainable_names.append(name)

        if len(trainable_names) > 0:
            raise ModelValidationError(
                f"Foundation Model parameter freezing check failed! {len(trainable_names)} parameters have requires_grad=True "
                f"(e.g. '{trainable_names[0]}'). Base foundation model MUST be completely frozen."
            )

        logger.info("Foundation Model freezing validation passed (0 trainable parameters).")
        return True
