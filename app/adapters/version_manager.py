"""DriftAdapt Adapter Version Manager.

Author: DriftAdapt Contributors
Purpose: Central singleton facade for immutable version control of LoRA adapters.
"""

import threading
from typing import Any, Dict, List, Optional

from app.adapters.exceptions import VersionAlreadyExists, VersionNotFound
from app.adapters.lifecycle import VersionLifecycleManager, VersionState
from app.adapters.metrics import AdapterMetricsPublisher
from app.adapters.rollback import RollbackEngine
from app.adapters.version_history import VersionHistoryManager
from app.adapters.version_metadata import AdapterVersionMetadata
from app.adapters.version_policy import VersionPolicyManager
from app.adapters.version_storage import VersionStorage
from app.core.logging.logger_factory import LoggerFactory


class AdapterVersionManager:
    """Thread-safe Singleton facade for immutable adapter versioning."""
    
    _instance: Optional["AdapterVersionManager"] = None
    _lock = threading.RLock()
    
    def __new__(cls) -> "AdapterVersionManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AdapterVersionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            with self._lock:
                if not hasattr(self, "_initialized"):
                    self._logger = LoggerFactory.get_logger("AdapterVersionManager")
                    self._metrics = AdapterMetricsPublisher()
                    self._policy = VersionPolicyManager()
                    self._storage = VersionStorage(
                        registry_file=self._policy.registry_file,
                        backup_directory=self._policy.backup_directory,
                        auto_backup=self._policy.auto_backup
                    )
                    self._history = VersionHistoryManager()
                    self._rollback = RollbackEngine()
                    
                    self._versions: Dict[str, AdapterVersionMetadata] = self._storage.load()
                    self._initialized = True
                    self._logger.info(f"Initialized VersionManager with {len(self._versions)} versions.")

    def create_version(self, metadata: AdapterVersionMetadata) -> AdapterVersionMetadata:
        """Creates a new immutable adapter version.
        
        Args:
            metadata: The initialized version metadata.
            
        Returns:
            The stored version metadata.
            
        Raises:
            VersionAlreadyExists: If a version with the same ID already exists.
            PolicyViolation: If adding this version violates a policy limit.
        """
        with self._lock:
            if metadata.version_id in self._versions:
                raise VersionAlreadyExists(f"Version {metadata.version_id} already exists.")
                
            clinic_history = self._history.get_history(self._versions, metadata.clinic_id)
            self._policy.enforce_clinic_limit(len(clinic_history))
            
            # Transition to active immediately after creation
            metadata.status = VersionLifecycleManager.transition(metadata.status, VersionState.ACTIVE.value)
            
            self._versions[metadata.version_id] = metadata
            
            if self._policy.auto_save:
                self._storage.save(self._versions)
                
            self._metrics.publish("adapter_version_created", 1)
            self._metrics.publish("adapter_version_count", len(self._versions))
            self._metrics.publish("storage_bytes", sum(v.adapter_size_bytes for v in self._versions.values()))
            
            self._logger.info(f"Created version {metadata.version_id}.")
            return metadata

    def get_version(self, version_id: str) -> AdapterVersionMetadata:
        """Retrieves a specific version."""
        with self._lock:
            v = self._versions.get(version_id)
            if not v:
                raise VersionNotFound(f"Version {version_id} not found.")
            return v

    def get_latest(self, clinic_id: str) -> Optional[AdapterVersionMetadata]:
        """Retrieves the latest version for a clinic."""
        with self._lock:
            return self._history.get_latest(self._versions, clinic_id)

    def get_previous(self, version_id: str) -> Optional[AdapterVersionMetadata]:
        """Retrieves the parent of a specific version."""
        with self._lock:
            return self._history.find_parent(self._versions, version_id)

    def rollback(self, clinic_id: str, target_version_id: str) -> AdapterVersionMetadata:
        """Rolls back a clinic to a previous version."""
        with self._lock:
            rolled_back = self._rollback.execute_rollback(self._versions, clinic_id, target_version_id)
            if self._policy.auto_save:
                self._storage.save(self._versions)
            return rolled_back

    def delete_version(self, version_id: str) -> AdapterVersionMetadata:
        """Soft deletes a version."""
        with self._lock:
            v = self.get_version(version_id)
            v.status = VersionLifecycleManager.transition(v.status, VersionState.DELETED.value)
            
            if self._policy.auto_save:
                self._storage.save(self._versions)
                
            self._metrics.publish("adapter_version_deleted", 1)
            self._logger.info(f"Soft deleted version {version_id}.")
            return v
            
    def list_versions(self, clinic_id: str) -> List[AdapterVersionMetadata]:
        """Returns all versions for a clinic."""
        with self._lock:
            return self._history.get_history(self._versions, clinic_id)
            
    def search_versions(
        self, 
        clinic_id: Optional[str] = None, 
        round_number: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[AdapterVersionMetadata]:
        """Searches versions based on criteria."""
        with self._lock:
            results = list(self._versions.values())
            if clinic_id:
                results = [v for v in results if v.clinic_id == clinic_id]
            if round_number is not None:
                results = [v for v in results if v.communication_round == round_number]
            if status:
                results = [v for v in results if v.status == status]
                
            return sorted(results, key=lambda v: v.created_at)
            
    def export_version(self, version_id: str) -> Dict[str, Any]:
        """Exports a version to a dictionary format."""
        return self.get_version(version_id).model_dump()
        
    def statistics(self) -> Dict[str, Any]:
        """Returns summary statistics of the version registry."""
        with self._lock:
            active = sum(1 for v in self._versions.values() if v.status == VersionState.ACTIVE)
            archived = sum(1 for v in self._versions.values() if v.status == VersionState.ARCHIVED)
            
            self._metrics.publish("active_versions", active)
            self._metrics.publish("archived_versions", archived)
            
            return {
                "total_versions": len(self._versions),
                "active_versions": active,
                "archived_versions": archived,
                "total_storage_bytes": sum(v.adapter_size_bytes for v in self._versions.values())
            }
