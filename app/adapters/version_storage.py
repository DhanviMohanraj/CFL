"""DriftAdapt Version Storage.

Author: DriftAdapt Contributors
Purpose: Manages JSON persistence of immutable version metadata.
"""

import json
import shutil
import threading
import time
from pathlib import Path
from typing import Dict

from app.adapters.version_metadata import AdapterVersionMetadata
from app.core.logging.logger_factory import LoggerFactory


class VersionStorage:
    """Thread-safe JSON storage for the version registry."""
    
    def __init__(self, registry_file: Path, backup_directory: Path, auto_backup: bool = True) -> None:
        self._registry_file = registry_file
        self._backup_directory = backup_directory
        self._auto_backup = auto_backup
        self._logger = LoggerFactory.get_logger("VersionStorage")
        self._lock = threading.RLock()
        
    def save(self, versions: Dict[str, AdapterVersionMetadata]) -> None:
        """Saves version metadata to disk with automated backup.
        
        Args:
            versions: Dictionary mapping version_id to AdapterVersionMetadata.
        """
        with self._lock:
            try:
                self._registry_file.parent.mkdir(parents=True, exist_ok=True)
                
                if self._auto_backup and self._registry_file.exists():
                    self._backup_directory.mkdir(parents=True, exist_ok=True)
                    timestamp = int(time.time())
                    bak_file = self._backup_directory / f"version_registry_{timestamp}.json.bak"
                    shutil.copy2(self._registry_file, bak_file)
                    
                data = {vid: v.model_dump() for vid, v in versions.items()}
                with open(self._registry_file, "w") as f:
                    json.dump(data, f, indent=4)
                    
            except Exception as e:
                self._logger.error(f"Failed to save version registry: {e}")
                
    def load(self) -> Dict[str, AdapterVersionMetadata]:
        """Loads version metadata from disk.
        
        Returns:
            Dictionary mapping version_id to AdapterVersionMetadata.
        """
        with self._lock:
            if not self._registry_file.exists():
                return {}
            try:
                with open(self._registry_file, "r") as f:
                    data = json.load(f)
                return {vid: AdapterVersionMetadata(**v) for vid, v in data.items()}
            except Exception as e:
                self._logger.error(f"Failed to load version registry: {e}")
                return {}
