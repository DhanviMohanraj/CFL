"""DriftAdapt Adapter Serializer.

Author: DriftAdapt Contributors
Purpose: Serializes adapter states to byte payloads for storage or transmission.
"""

import io
import time
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import torch
except ImportError:
    torch = None

from app.adapters.exceptions import (
    DeserializationError,
    SerializationError,
    UnsupportedFormat,
)
from app.adapters.metrics import AdapterMetricsPublisher
from app.core.config.config_manager import ConfigManager
from app.core.logging.logger_factory import LoggerFactory


class AdapterSerializer:
    """Handles serialization and deserialization of adapter states."""
    
    def __init__(self, configs_dir: Optional[Path] = None) -> None:
        """Initializes the serializer from configuration."""
        self._logger = LoggerFactory.get_logger("AdapterSerializer")
        self._metrics = AdapterMetricsPublisher()
        
        config = ConfigManager(configs_dir=configs_dir).get_config()
        try:
            adapter_state_config = getattr(config, "adapter_state", None)
            self._format = getattr(adapter_state_config, "serializer", "torch")
            self._compression = getattr(adapter_state_config, "compression", False)
        except AttributeError:
            self._format = "torch"
            self._compression = False
            
        if self._format != "torch":
            raise UnsupportedFormat(f"Format {self._format} is not supported.")
            
    def serialize(self, state_dict: Dict[str, Any]) -> bytes:
        """Serializes a state dictionary to bytes.
        
        Args:
            state_dict: Dictionary mapping parameter names to tensors.
            
        Returns:
            The serialized byte payload.
            
        Raises:
            SerializationError: If serialization fails.
        """
        if torch is None:
            raise SerializationError("PyTorch is required for serialization.")
            
        start_time = time.perf_counter()
        buffer = io.BytesIO()
        
        try:
            # We don't have native zip compression toggles here in standard save without
            # altering the zipfile layout manually, but we rely on torch.save.
            torch.save(state_dict, buffer)
            data = buffer.getvalue()
        except Exception as e:
            self._logger.error(f"Serialization failed: {e}")
            raise SerializationError(f"Serialization failed: {e}")
        
        duration = (time.perf_counter() - start_time) * 1000
        size_bytes = len(data)
        
        self._metrics.publish("serialization_time", duration)
        self._metrics.publish("adapter_size_bytes", size_bytes)
        self._metrics.publish("adapter_size_mb", size_bytes / (1024 * 1024))
        self._metrics.publish("communication_payload", size_bytes)
        
        self._logger.debug(f"Serialized {len(state_dict)} parameters into {size_bytes} bytes in {duration:.2f}ms")
        
        return data
        
    def deserialize(self, data: bytes) -> Dict[str, Any]:
        """Deserializes a byte payload back to a state dictionary.
        
        Args:
            data: Serialized byte payload.
            
        Returns:
            Dictionary mapping parameter names to tensors.
            
        Raises:
            DeserializationError: If deserialization fails.
        """
        if torch is None:
            raise DeserializationError("PyTorch is required for deserialization.")
            
        start_time = time.perf_counter()
        buffer = io.BytesIO(data)
        
        try:
            # Map location cpu prevents GPU OOM if loading multiple states concurrently
            state_dict = torch.load(buffer, map_location="cpu", weights_only=True)
        except Exception as e:
            # Fallback for older torch versions if weights_only fails
            try:
                buffer.seek(0)
                state_dict = torch.load(buffer, map_location="cpu")
            except Exception as e2:
                self._logger.error(f"Deserialization failed: {e2}")
                raise DeserializationError(f"Deserialization failed: {e2}")
            
        duration = (time.perf_counter() - start_time) * 1000
        self._metrics.publish("deserialization_time", duration)
        
        if not isinstance(state_dict, dict):
            raise DeserializationError(f"Expected dict, got {type(state_dict)}")
            
        self._logger.debug(f"Deserialized {len(state_dict)} parameters in {duration:.2f}ms")
        return state_dict
        
    def save(self, state_dict: Dict[str, Any], file_path: Path) -> None:
        """Serializes and saves a state directly to disk."""
        data = self.serialize(state_dict)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        self._logger.info(f"Saved adapter state to {file_path}")
        
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Loads and deserializes a state directly from disk."""
        if not file_path.exists():
            raise FileNotFoundError(f"Adapter file not found: {file_path}")
        data = file_path.read_bytes()
        state_dict = self.deserialize(data)
        self._logger.info(f"Loaded adapter state from {file_path}")
        return state_dict
        
    def estimate_size(self, state_dict: Dict[str, Any]) -> int:
        """Estimates byte size via fast serialization."""
        data = self.serialize(state_dict)
        return len(data)
