"""DriftAdapt Cache Manager Module.

Author: DriftAdapt Contributors
Purpose: Manages model weight caching directories, cache hit checks, size calculations, and cleaning.
Future Integration: Invoked by DownloadManager and ModelLoader.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config.loader import get_project_root
from app.core.logging import LoggerFactory
from app.models.foundation.exceptions import CacheError

logger = LoggerFactory.get_logger("CacheManager")


class CacheManager:
    """Manages model weight cache locations, storage sizes, and cache checks."""

    def __init__(self, custom_cache_dir: Optional[str] = None) -> None:
        """Initializes CacheManager.

        Args:
            custom_cache_dir: Custom path to cache directory. Defaults to 'models/cache'.
        """
        if custom_cache_dir:
            self._cache_dir = Path(custom_cache_dir).resolve()
        else:
            self._cache_dir = (get_project_root() / "models" / "cache").resolve()

        # Ensure cache directory exists
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"CacheManager initialized. Target cache path: {self._cache_dir}")

    @property
    def cache_dir(self) -> Path:
        """Returns the resolved cache directory Path object."""
        return self._cache_dir

    def resolve_model_cache_path(self, model_name: str) -> Path:
        """Resolves target directory for a specific model inside cache."""
        sanitized = model_name.replace("/", "--").replace("\\", "--")
        return self._cache_dir / sanitized

    def is_cached(self, model_name: str) -> bool:
        """Checks if a model directory exists in cache and contains weight files."""
        # 1. Direct path check
        if os.path.exists(model_name) and os.path.isdir(model_name):
            return True

        # 2. Sanitized directory inside cache_dir
        model_path = self.resolve_model_cache_path(model_name)
        if model_path.exists() and model_path.is_dir():
            # Check if directory contains config or weight files
            contents = list(model_path.glob("*"))
            if len(contents) > 0:
                logger.info(f"Cache hit for model '{model_name}' at: {model_path}")
                return True

        # 3. Check HuggingFace default cache layout (hub/models--...)
        hf_layout = self._cache_dir / "hub" / f"models--{model_name.replace('/', '--')}"
        if hf_layout.exists() and hf_layout.is_dir():
            snapshots = hf_layout / "snapshots"
            if snapshots.exists() and len(list(snapshots.glob("*"))) > 0:
                logger.info(f"Cache hit (HF Hub layout) for model '{model_name}' at: {hf_layout}")
                return True

        logger.info(f"Cache miss for model '{model_name}'.")
        return False


    def get_cache_size_bytes(self) -> int:
        """Calculates total disk space occupied by cache in bytes."""
        total_bytes = 0
        try:
            for root, _, files in os.walk(self._cache_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    if os.path.exists(fp):
                        total_bytes += os.path.getsize(fp)
        except Exception as e:
            logger.warning(f"Failed to compute cache size: {e}")
        return total_bytes

    def get_cache_size_mb(self) -> float:
        """Returns total disk space occupied by cache in Megabytes (MB)."""
        return round(self.get_cache_size_bytes() / (1024 * 1024), 2)

    def list_cached_models(self) -> List[Dict[str, Any]]:
        """Returns a list of all model directories stored in cache with their disk sizes."""
        results: List[Dict[str, Any]] = []
        if not self._cache_dir.exists():
            return results

        try:
            for item in self._cache_dir.iterdir():
                if item.is_dir():
                    folder_size = 0
                    for root, _, files in os.walk(item):
                        for f in files:
                            fp = os.path.join(root, f)
                            if os.path.exists(fp):
                                folder_size += os.path.getsize(fp)
                    results.append(
                        {
                            "name": item.name.replace("--", "/"),
                            "path": str(item),
                            "size_mb": round(folder_size / (1024 * 1024), 2),
                        }
                    )
        except Exception as e:
            logger.warning(f"Failed to list cached models: {e}")
        return results

    def clear_cache(self, model_name: Optional[str] = None) -> bool:
        """Cleans specific model cache entry or wipes the entire cache directory.

        Args:
            model_name: Optional model name to delete. If None, clears all cache contents.

        Returns:
            bool: True if clean operation succeeded.
        """
        try:
            if model_name:
                target_path = self.resolve_model_cache_path(model_name)
                if target_path.exists():
                    shutil.rmtree(target_path)
                    logger.info(f"Cleared cache for model '{model_name}'.")
                    return True
                return False

            # Wipe all cache
            for item in self._cache_dir.iterdir():
                if item.name == ".gitkeep":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            logger.info("Cleared entire model cache directory.")
            return True
        except Exception as e:
            raise CacheError(f"Failed to clear model cache: {e}") from e
