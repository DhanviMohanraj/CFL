"""DriftAdapt Download Manager Module.

Author: DriftAdapt Contributors
Purpose: Manages model weight downloading from HuggingFace Hub, resume capability, and offline checks.
Future Integration: Invoked by ModelLoader before loading model weights.
"""

import os
from pathlib import Path
from typing import Optional

from app.core.logging import LoggerFactory
from app.models.foundation.cache_manager import CacheManager
from app.models.foundation.exceptions import DownloadError

logger = LoggerFactory.get_logger("DownloadManager")

try:
    from huggingface_hub import hf_hub_download, snapshot_download  # noqa: F401
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False


class DownloadManager:
    """Manages HuggingFace model weight downloads, offline mode, and resume capabilities."""

    def __init__(self, cache_manager: Optional[CacheManager] = None) -> None:
        """Initializes DownloadManager."""
        self._cache_manager = cache_manager or CacheManager()

    @staticmethod
    def is_offline_mode() -> bool:
        """Returns True if system is running in offline mode (HF_HUB_OFFLINE=1 or TRANSFORMERS_OFFLINE=1)."""
        env_hf = os.environ.get("HF_HUB_OFFLINE", "0").lower().strip()
        env_tf = os.environ.get("TRANSFORMERS_OFFLINE", "0").lower().strip()
        return env_hf in ("1", "true", "yes") or env_tf in ("1", "true", "yes")

    def download_model(
        self,
        model_name: str,
        revision: str = "main",
        force_download: bool = False,
        resume_download: bool = True,
    ) -> Path:
        """Downloads model repository files to cache directory.

        Args:
            model_name: HuggingFace model identifier (e.g. 'Qwen/Qwen2.5-3B-Instruct').
            revision: Specific git tag or commit branch.
            force_download: If True, re-downloads even if cached.
            resume_download: If True, resumes incomplete downloads.

        Returns:
            Path: Path to local downloaded model snapshot.

        Raises:
            DownloadError: If download fails or offline mode blocks download.
        """
        # 1. Check if model is already local path
        if os.path.exists(model_name) and os.path.isdir(model_name):
            logger.info(f"Model path '{model_name}' exists on local filesystem.")
            return Path(model_name)

        # 2. Check offline mode
        offline = self.is_offline_mode()
        cached = self._cache_manager.is_cached(model_name)

        if offline and not cached:
            raise DownloadError(
                f"Offline mode is ACTIVE (HF_HUB_OFFLINE=1), but model '{model_name}' is not present in local cache. "
                "Disable offline mode or pre-download model weights before running."
            )

        if cached and not force_download:
            logger.info(f"Model '{model_name}' found in local cache. Skipping download.")
            return self._cache_manager.resolve_model_cache_path(model_name)

        # 3. Perform download via huggingface_hub snapshot_download
        if not HAS_HF_HUB:
            logger.warning(
                "huggingface_hub package is not installed. Unable to trigger snapshot_download. "
                "Relying on AutoModel.from_pretrained() internal download pipeline."
            )
            return self._cache_manager.resolve_model_cache_path(model_name)

        logger.info(f"Initiating snapshot download for model '{model_name}' to cache: {self._cache_manager.cache_dir}")

        try:
            download_dir = snapshot_download(
                repo_id=model_name,
                revision=revision,
                cache_dir=str(self._cache_manager.cache_dir),
                resume_download=resume_download,
                force_download=force_download,
                local_files_only=offline,
            )
            logger.info(f"Successfully downloaded model snapshot '{model_name}' to: {download_dir}")
            return Path(download_dir)
        except Exception as e:
            logger.error(f"Download failed for model '{model_name}': {e}")
            raise DownloadError(f"Failed to download foundation model '{model_name}': {e}") from e
