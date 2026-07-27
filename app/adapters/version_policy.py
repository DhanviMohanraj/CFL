"""DriftAdapt Version Policy Manager.

Author: DriftAdapt Contributors
Purpose: Enforces storage and retention policies for version history.
"""

from pathlib import Path
from typing import Optional

from app.adapters.exceptions import PolicyViolation
from app.core.config.config_manager import ConfigManager
from app.core.logging.logger_factory import LoggerFactory


class VersionPolicyManager:
    """Loads and enforces versioning rules."""
    
    def __init__(self, configs_dir: Optional[Path] = None) -> None:
        """Initializes the policy manager and loads rules from config."""
        self._logger = LoggerFactory.get_logger("VersionPolicyManager")
        config = ConfigManager(configs_dir=configs_dir).get_config()
        
        # Defaults
        self.max_versions_per_clinic: int = 100
        self.retention_policy: str = "archive"
        self.checksum_validation: bool = True
        self.auto_save: bool = True
        self.registry_file: Path = Path("data/version_registry.json")
        self.backup_directory: Path = Path("data/backups")
        self.auto_backup: bool = True
        
        try:
            adapter_config = getattr(config, "adapter_versioning", None)
            if adapter_config is not None:
                self.max_versions_per_clinic = getattr(adapter_config, "max_versions_per_clinic", self.max_versions_per_clinic)
                self.retention_policy = getattr(adapter_config, "retention_policy", self.retention_policy)
                self.checksum_validation = getattr(adapter_config, "checksum_validation", self.checksum_validation)
                self.auto_save = getattr(adapter_config, "auto_save", self.auto_save)
                self.auto_backup = getattr(adapter_config, "auto_backup", self.auto_backup)
                
                reg_file = getattr(adapter_config, "registry_file", str(self.registry_file))
                self.registry_file = Path(reg_file)
                
                bak_dir = getattr(adapter_config, "backup_directory", str(self.backup_directory))
                self.backup_directory = Path(bak_dir)
        except Exception as e:
            self._logger.warning(f"Failed to load specific versioning policy, using defaults: {e}")

    def enforce_clinic_limit(self, clinic_version_count: int) -> None:
        """Raises a PolicyViolation if adding a new version would exceed limits."""
        if clinic_version_count >= self.max_versions_per_clinic:
            raise PolicyViolation(
                f"Clinic limit of {self.max_versions_per_clinic} versions reached. "
                "Must archive or delete old versions before creating new ones."
            )
