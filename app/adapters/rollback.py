"""DriftAdapt Rollback Engine.

Author: DriftAdapt Contributors
Purpose: Facilitates rolling back clinic states to historical adapter versions securely.
"""

from typing import Callable, Dict, Optional

from app.adapters.exceptions import RollbackFailed, VersionNotFound
from app.adapters.lifecycle import VersionLifecycleManager, VersionState
from app.adapters.metrics import AdapterMetricsPublisher
from app.adapters.version_metadata import AdapterVersionMetadata
from app.core.logging.logger_factory import LoggerFactory


class RollbackEngine:
    """Coordinates secure and validated version rollbacks."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("RollbackEngine")
        self._metrics = AdapterMetricsPublisher()

    def execute_rollback(
        self, 
        versions: Dict[str, AdapterVersionMetadata], 
        clinic_id: str, 
        target_version_id: str,
        verify_checksum_fn: Optional[Callable[[AdapterVersionMetadata], bool]] = None
    ) -> AdapterVersionMetadata:
        """Executes a rollback for a clinic to a specific version.
        
        Args:
            versions: The complete dictionary of versions.
            clinic_id: The clinic attempting the rollback.
            target_version_id: The ID to rollback to.
            verify_checksum_fn: Optional dependency injected function to physically verify weights on disk.
            
        Returns:
            The rolled-back version metadata.
            
        Raises:
            VersionNotFound: If the target does not exist.
            RollbackFailed: If verification fails, ownership fails, or state transition fails.
        """
        target = versions.get(target_version_id)
        if not target:
            raise VersionNotFound(f"Cannot rollback to {target_version_id}, version not found.")
            
        if target.clinic_id != clinic_id:
            raise RollbackFailed(f"Version {target_version_id} does not belong to clinic {clinic_id}.")
            
        if target.status == VersionState.DELETED:
            raise RollbackFailed(f"Cannot rollback to deleted version {target_version_id}.")

        # Perform external physical checksum validation if injected
        if verify_checksum_fn is not None and not verify_checksum_fn(target):
            raise RollbackFailed(f"Checksum verification failed for physical payload of {target_version_id}.")

        # Advance state to ROLLED_BACK via lifecycle manager validation
        try:
            target.status = VersionLifecycleManager.transition(target.status, VersionState.ROLLED_BACK.value)
        except Exception as e:
            raise RollbackFailed(f"Illegal state transition during rollback: {e}")
        
        self._metrics.publish("rollback_count", 1)
        self._metrics.publish("adapter_version_restored", 1)
        self._logger.info(f"Successfully rolled back clinic {clinic_id} to version {target_version_id}.")
        
        return target
