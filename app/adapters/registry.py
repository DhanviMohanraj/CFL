"""DriftAdapt Adapter Registry Module.

Author: DriftAdapt Contributors
Purpose: Core singleton registry managing clinic-owned federated LoRA adapters.
"""

import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.adapters.adapter_info import AdapterInfo
from app.adapters.enums import AdapterStatus
from app.adapters.exceptions import (
    AdapterAlreadyExists,
    AdapterNotFound,
    ClinicNotFound,
    InvalidClinicID,
    RegistryPersistenceError,
)
from app.adapters.storage import read_json_file, write_json_file
from app.core.config.config_manager import ConfigManager
from app.core.logging.logger_factory import LoggerFactory
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType
from app.core.metrics.metrics_bus import MetricsBus


class AdapterRegistry:
    """Singleton registry for managing federated adapters metadata."""

    _instance: Optional["AdapterRegistry"] = None
    _singleton_lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "AdapterRegistry":
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, configs_dir: Optional[Path] = None) -> None:
        """Initializes the registry, loading config and metrics."""
        if getattr(self, "_initialized", False):
            return

        self._lock = threading.RLock()
        self._adapters: Dict[str, AdapterInfo] = {}

        # Dependencies
        self._configs_dir = configs_dir
        self._config_manager = ConfigManager(configs_dir=configs_dir)
        self._logger = LoggerFactory.get_logger("AdapterRegistry")
        self._metrics_bus = MetricsBus(configs_dir=configs_dir)

        # Configuration loading
        config = self._config_manager.get_config()
        
        # Try to read adapter_registry settings, fallback to defaults if not in schema
        try:
            reg_config = getattr(config, "adapter_registry", None)
            self._registry_path = Path(getattr(reg_config, "registry_path", "data/registry.json"))
            self._autosave = getattr(reg_config, "autosave", True)
            self._backup = getattr(reg_config, "backup", True)
        except AttributeError:
            self._registry_path = Path("data/registry.json")
            self._autosave = True
            self._backup = True

        self._register_metrics()
        self.load_registry()

        self._logger.info("AdapterRegistry initialized.")
        self._initialized = True

    def _register_metrics(self) -> None:
        """Registers telemetry schemas used by the AdapterRegistry."""
        try:
            self._metrics_bus.register_schema(
                "adapter_registered", MetricType.PERSONALIZATION, "Count of adapters registered."
            )
            self._metrics_bus.register_schema(
                "adapter_deleted", MetricType.PERSONALIZATION, "Count of adapters deleted."
            )
            self._metrics_bus.register_schema(
                "adapter_activated", MetricType.PERSONALIZATION, "Count of adapters activated."
            )
            self._metrics_bus.register_schema(
                "adapter_loaded", MetricType.PERSONALIZATION, "Registry load events."
            )
            self._metrics_bus.register_schema(
                "adapter_count", MetricType.PERSONALIZATION, "Total active adapters."
            )
            self._metrics_bus.register_schema(
                "clinic_count", MetricType.FEDERATION, "Total clinics in registry."
            )
        except Exception as e:
            self._logger.warning(f"Failed to register metrics schemas: {e}")

    def _check_clinic_id(self, clinic_id: str) -> None:
        """Validates clinic_id format."""
        if not clinic_id or not str(clinic_id).strip() or clinic_id == "None":
            raise InvalidClinicID(f"Invalid clinic_id: '{clinic_id}'")
        if not clinic_id.replace("_", "").isalnum():
            raise InvalidClinicID(f"Invalid clinic_id format: '{clinic_id}'")

    def register(
        self,
        clinic_id: str,
        adapter_name: str,
        round_number: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AdapterInfo:
        """Registers a new adapter."""
        self._check_clinic_id(clinic_id)
        if round_number < 1:
            raise ValueError("Round number must be >= 1")

        with self._lock:
            # Ensure uniqueness
            for adapter in self._adapters.values():
                if (
                    adapter.clinic_id == clinic_id
                    and adapter.adapter_name == adapter_name
                    and adapter.round_number == round_number
                ):
                    raise AdapterAlreadyExists(
                        f"Adapter {adapter_name} for clinic {clinic_id} at round {round_number} already exists."
                    )

            try:
                adapter_info = AdapterInfo(
                    clinic_id=clinic_id,
                    adapter_name=adapter_name,
                    round_number=round_number,
                    metadata=metadata or {},
                )
            except ValidationError as e:
                raise InvalidClinicID(f"Validation error: {e}")

            self._adapters[adapter_info.adapter_id] = adapter_info
            
            # Save and publish
            if self._autosave:
                self.save_registry()

            self._publish_metric("adapter_registered", 1)
            self._logger.info(
                f"Registered adapter: {adapter_info.adapter_id} for clinic {clinic_id}"
            )
            return adapter_info

    def get(
        self,
        adapter_id: Optional[str] = None,
        clinic_id: Optional[str] = None,
        adapter_name: Optional[str] = None,
    ) -> AdapterInfo:
        """Retrieves an adapter by ID or by clinic_id + adapter_name."""
        with self._lock:
            if adapter_id:
                if adapter_id not in self._adapters:
                    raise AdapterNotFound(f"Adapter with ID {adapter_id} not found.")
                adapter = self._adapters[adapter_id]
                if adapter.status == AdapterStatus.DELETED:
                    raise AdapterNotFound(f"Adapter with ID {adapter_id} is deleted.")
                return adapter

            if clinic_id and adapter_name:
                for adapter in self._adapters.values():
                    if (
                        adapter.clinic_id == clinic_id
                        and adapter.adapter_name == adapter_name
                        and adapter.status != AdapterStatus.DELETED
                    ):
                        return adapter
                raise AdapterNotFound(
                    f"Adapter {adapter_name} for clinic {clinic_id} not found."
                )

            raise ValueError("Must provide adapter_id or (clinic_id and adapter_name)")

    def exists(
        self,
        adapter_id: Optional[str] = None,
        clinic_id: Optional[str] = None,
        adapter_name: Optional[str] = None,
    ) -> bool:
        """Checks if an adapter exists."""
        try:
            self.get(adapter_id=adapter_id, clinic_id=clinic_id, adapter_name=adapter_name)
            return True
        except AdapterNotFound:
            return False

    def activate(self, adapter_id: str) -> None:
        """Activates an adapter and deactivates any currently active one for the same clinic."""
        with self._lock:
            target = self.get(adapter_id=adapter_id)
            clinic_id = target.clinic_id

            # Deactivate others
            for adapter in self._adapters.values():
                if adapter.clinic_id == clinic_id and adapter.is_active:
                    adapter.status = AdapterStatus.INACTIVE
                    adapter.is_active = False
                    adapter.updated_at = time.time()

            target.status = AdapterStatus.ACTIVE
            target.is_active = True
            target.updated_at = time.time()

            if self._autosave:
                self.save_registry()

            self._publish_metric("adapter_activated", 1, client_id=clinic_id)
            self._logger.info(f"Activated adapter {adapter_id} for clinic {clinic_id}")

    def deactivate(self, adapter_id: str) -> None:
        """Deactivates an adapter."""
        with self._lock:
            target = self.get(adapter_id=adapter_id)
            if target.is_active:
                target.status = AdapterStatus.INACTIVE
                target.is_active = False
                target.updated_at = time.time()

                if self._autosave:
                    self.save_registry()
                self._logger.info(f"Deactivated adapter {adapter_id}")

    def delete(self, adapter_id: str) -> None:
        """Soft-deletes an adapter."""
        with self._lock:
            target = self.get(adapter_id=adapter_id)
            target.status = AdapterStatus.DELETED
            target.is_active = False
            target.updated_at = time.time()

            if self._autosave:
                self.save_registry()
            
            self._publish_metric("adapter_deleted", 1, client_id=target.clinic_id)
            self._logger.info(f"Deleted adapter {adapter_id}")

    def get_latest(self, clinic_id: str) -> AdapterInfo:
        """Returns the adapter with the highest round_number for a clinic."""
        self._check_clinic_id(clinic_id)
        with self._lock:
            clinic_adapters = self.list_by_clinic(clinic_id)
            if not clinic_adapters:
                raise ClinicNotFound(f"No adapters found for clinic {clinic_id}")
            
            latest = max(clinic_adapters, key=lambda a: a.round_number)
            return latest

    def list_all(self) -> List[AdapterInfo]:
        """Lists all non-deleted adapters."""
        with self._lock:
            return [a for a in self._adapters.values() if a.status != AdapterStatus.DELETED]

    def list_by_clinic(self, clinic_id: str) -> List[AdapterInfo]:
        """Lists non-deleted adapters for a specific clinic."""
        self._check_clinic_id(clinic_id)
        with self._lock:
            return [
                a for a in self._adapters.values()
                if a.clinic_id == clinic_id and a.status != AdapterStatus.DELETED
            ]

    def list_by_round(self, round_number: int) -> List[AdapterInfo]:
        """Lists non-deleted adapters for a specific round."""
        with self._lock:
            return [
                a for a in self._adapters.values()
                if a.round_number == round_number and a.status != AdapterStatus.DELETED
            ]

    def list_active(self) -> List[AdapterInfo]:
        """Lists all currently active adapters."""
        with self._lock:
            return [a for a in self._adapters.values() if a.is_active and a.status != AdapterStatus.DELETED]

    def list_inactive(self) -> List[AdapterInfo]:
        """Lists all inactive adapters."""
        with self._lock:
            return [
                a for a in self._adapters.values()
                if not a.is_active and a.status not in (AdapterStatus.DELETED, AdapterStatus.ACTIVE)
            ]

    def statistics(self) -> Dict[str, Any]:
        """Returns registry statistics."""
        with self._lock:
            total_adapters = len(self._adapters)
            active = len([a for a in self._adapters.values() if a.is_active])
            deleted = len([a for a in self._adapters.values() if a.status == AdapterStatus.DELETED])
            
            clinic_set = {a.clinic_id for a in self._adapters.values() if a.status != AdapterStatus.DELETED}
            total_clinics = len(clinic_set)
            
            active_list = [a for a in self._adapters.values() if a.status != AdapterStatus.DELETED]
            latest_round = max((a.round_number for a in active_list), default=0)
            
            avg_adapters = (len(active_list) / total_clinics) if total_clinics > 0 else 0.0

            stats = {
                "total_clinics": total_clinics,
                "total_adapters": total_adapters,
                "active_adapters": active,
                "deleted_adapters": deleted,
                "latest_round": latest_round,
                "average_adapters_per_clinic": avg_adapters,
            }

            self._publish_metric("adapter_count", total_adapters)
            self._publish_metric("clinic_count", total_clinics)
            
            return stats

    def clear(self) -> None:
        """Clears the registry (in memory)."""
        with self._lock:
            self._adapters.clear()
            self._logger.info("Registry cleared.")

    def export_registry(self) -> Dict[str, Any]:
        """Exports the entire registry state as a dict."""
        with self._lock:
            return {
                "adapters": {
                    aid: a.model_dump() for aid, a in self._adapters.items()
                }
            }

    def import_registry(self, data: Dict[str, Any]) -> None:
        """Imports registry state from a dict, overwriting current state."""
        with self._lock:
            self.clear()
            adapters_data = data.get("adapters", {})
            for aid, adata in adapters_data.items():
                try:
                    self._adapters[aid] = AdapterInfo(**adata)
                except ValidationError as e:
                    self._logger.error(f"Failed to import adapter {aid}: {e}")
            
            if self._autosave:
                self.save_registry()
            self._logger.info(f"Imported {len(self._adapters)} adapters.")

    def load_registry(self) -> None:
        """Loads registry state from disk."""
        with self._lock:
            try:
                data = read_json_file(self._registry_path)
                if data:
                    self.import_registry(data)
                self._publish_metric("adapter_loaded", 1)
            except Exception as e:
                self._logger.error(f"Failed to load registry: {e}")
                raise RegistryPersistenceError(f"Failed to load registry: {e}")

    def save_registry(self) -> None:
        """Saves registry state to disk."""
        with self._lock:
            try:
                data = self.export_registry()
                write_json_file(self._registry_path, data)
                if self._backup:
                    backup_path = self._registry_path.with_suffix(".json.bak")
                    write_json_file(backup_path, data)
            except Exception as e:
                self._logger.error(f"Failed to save registry: {e}")
                raise RegistryPersistenceError(f"Failed to save registry: {e}")

    def _publish_metric(self, name: str, value: Any, client_id: Optional[str] = None) -> None:
        """Helper to publish metrics."""
        try:
            metric = Metric(
                name=name,
                value=value,
                module="AdapterRegistry",
                client_id=client_id
            )
            self._metrics_bus.publish(metric)
        except Exception as e:
            self._logger.warning(f"Failed to publish metric {name}: {e}")
