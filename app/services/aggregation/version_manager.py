"""Version Manager Service.

Author: DriftAdapt Contributors
Purpose: Manages global adapter versions, tracks lineages, and resolves rollback operations.
"""

from typing import List, Optional
from datetime import datetime

from app.core.logging import LoggerFactory


class VersionManager:
    """Manages adapter versions systematically."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("VersionManager")
        # In-memory history for active versions.
        # Format: list of version tags in chronological order.
        self._versions: List[str] = []

    def generate_next_version(self, communication_round: int) -> str:
        """Generates a standardized version tag for the new round.
        
        Args:
            communication_round: The federated learning round.
            
        Returns:
            A string version tag, e.g., 'v1.0.0-round5'.
        """
        version_tag = f"v1.0.0-round{communication_round}"
        self._versions.append(version_tag)
        self._logger.info(f"Generated new global adapter version: {version_tag}")
        return version_tag

    def get_latest_version(self) -> Optional[str]:
        """Retrieves the most recent version tag."""
        if not self._versions:
            return None
        return self._versions[-1]

    def get_version_history(self) -> List[str]:
        """Returns the chronological list of all versions."""
        return self._versions.copy()

    def rollback_version(self, target_version: Optional[str] = None) -> Optional[str]:
        """Rolls back the system to a previous version.
        
        Args:
            target_version: Specific version to rollback to. If None, rolls back exactly one version.
            
        Returns:
            The newly active version tag, or None if rollback failed.
        """
        if not self._versions:
            self._logger.warning("No versions to rollback.")
            return None
            
        if target_version is None:
            if len(self._versions) > 1:
                dropped = self._versions.pop()
                self._logger.info(f"Rolled back 1 version (dropped {dropped}).")
                return self._versions[-1]
            else:
                self._logger.warning("Cannot rollback; only one version exists.")
                return None
                
        if target_version in self._versions:
            idx = self._versions.index(target_version)
            self._versions = self._versions[:idx + 1]
            self._logger.info(f"Rolled back to specific version {target_version}.")
            return self._versions[-1]
            
        self._logger.error(f"Target version {target_version} not found in history.")
        return None
