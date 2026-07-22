"""DriftAdapt Tokenizer Loader Module.

Author: DriftAdapt Contributors
Purpose: Loads HuggingFace AutoTokenizer, configures pad/eos tokens, and checks compatibility.
Future Integration: Invoked by ModelFactory and ModelManager.
"""

import time
from typing import Any, Dict, Optional

from app.core.logging import LoggerFactory
from app.models.foundation.exceptions import TokenizerLoadError
from app.models.foundation.interfaces import TokenizerLoaderInterface

logger = LoggerFactory.get_logger("TokenizerLoader")

try:
    from transformers import AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class TokenizerLoader(TokenizerLoaderInterface):
    """Loads and configures tokenizers for foundation language models."""

    def load_tokenizer(
        self,
        tokenizer_name_or_path: str,
        cache_dir: Optional[str] = None,
        use_fast: bool = True,
    ) -> Any:
        """Loads and returns a tokenizer instance.

        Args:
            tokenizer_name_or_path: Repository name or local path.
            cache_dir: Optional local cache directory path.
            use_fast: If True, uses fast Rust-backed tokenizer when available.

        Returns:
            Any: Configured HuggingFace PreTrainedTokenizer or AutoTokenizer.

        Raises:
            TokenizerLoadError: If loading fails or transformers is missing.
        """
        start_time = time.time()
        logger.info(f"Loading tokenizer for target: '{tokenizer_name_or_path}' (use_fast={use_fast})")

        if not HAS_TRANSFORMERS:
            raise TokenizerLoadError(
                "Package 'transformers' is not installed. Unable to load AutoTokenizer. "
                "Install via 'pip install transformers'."
            )

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                tokenizer_name_or_path,
                cache_dir=cache_dir,
                use_fast=use_fast,
                trust_remote_code=True,
            )

            # Ensure pad_token is configured
            if tokenizer.pad_token is None:
                if tokenizer.eos_token is not None:
                    tokenizer.pad_token = tokenizer.eos_token
                    logger.info(f"Configured missing pad_token using eos_token ('{tokenizer.eos_token}').")
                else:
                    tokenizer.add_special_tokens({"pad_token": "[PAD]"})
                    logger.info("Added new default '[PAD]' special token to tokenizer.")

            elapsed = time.time() - start_time
            vocab_size = getattr(tokenizer, "vocab_size", len(tokenizer))
            logger.info(
                f"Tokenizer '{tokenizer_name_or_path}' loaded successfully in {elapsed:.2f}s "
                f"(vocab_size={vocab_size:,}, is_fast={getattr(tokenizer, 'is_fast', False)})."
            )
            return tokenizer

        except Exception as e:
            logger.error(f"Failed to load tokenizer '{tokenizer_name_or_path}': {e}")
            raise TokenizerLoadError(f"Error loading tokenizer '{tokenizer_name_or_path}': {e}") from e

    @staticmethod
    def get_tokenizer_summary(tokenizer: Any) -> Dict[str, Any]:
        """Extracts key vocabulary and special token metadata from a tokenizer."""
        if tokenizer is None:
            return {}

        return {
            "vocab_size": getattr(tokenizer, "vocab_size", 0),
            "is_fast": getattr(tokenizer, "is_fast", False),
            "bos_token": str(getattr(tokenizer, "bos_token", None)),
            "eos_token": str(getattr(tokenizer, "eos_token", None)),
            "pad_token": str(getattr(tokenizer, "pad_token", None)),
            "unk_token": str(getattr(tokenizer, "unk_token", None)),
            "model_max_length": getattr(tokenizer, "model_max_length", 2048),
        }
