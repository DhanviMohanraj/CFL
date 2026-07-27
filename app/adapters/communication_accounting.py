"""DriftAdapt Communication Accounting Engine.

Author: DriftAdapt Contributors
Purpose: Estimates payload sizes and latency based on adapter properties.
"""

from typing import Any, Dict

from app.adapters.metrics_exceptions import CommunicationEstimationError
from app.adapters.metrics_schema import AdapterMetrics


class CommunicationAccounting:
    """Estimates network usage for federated synchronization."""

    BANDWIDTH_PROFILES = {
        "wifi": 50 * 1024 * 1024,      # 50 MB/s
        "4g": 10 * 1024 * 1024,        # 10 MB/s
        "5g": 100 * 1024 * 1024,       # 100 MB/s
        "satellite": 1 * 1024 * 1024,  # 1 MB/s
        "offline": 0                   # No network
    }
    
    def __init__(self, profile_name: str = "wifi", compression_enabled: bool = True) -> None:
        self._profile = profile_name.lower()
        self._compression = compression_enabled
        self._bandwidth = self.BANDWIDTH_PROFILES.get(self._profile, self.BANDWIDTH_PROFILES["wifi"])
        
    def estimate_upload(self, adapter: AdapterMetrics) -> int:
        """Estimates bytes required to upload an adapter."""
        try:
            return adapter.compressed_size_bytes if self._compression else adapter.serialized_size_bytes
        except Exception as e:
            raise CommunicationEstimationError(f"Failed to estimate upload: {e}")
            
    def estimate_download(self, adapter: AdapterMetrics) -> int:
        """Estimates bytes required to download an adapter."""
        try:
            return adapter.compressed_size_bytes if self._compression else adapter.serialized_size_bytes
        except Exception as e:
            raise CommunicationEstimationError(f"Failed to estimate download: {e}")
            
    def estimate_latency(self, bytes_to_transfer: int) -> float:
        """Estimates network transmission time in milliseconds."""
        if self._bandwidth <= 0:
            return 0.0  # Offline
        return (bytes_to_transfer / self._bandwidth) * 1000.0

    def estimate_round_cost(self, num_clients: int, average_adapter: AdapterMetrics) -> Dict[str, Any]:
        """Estimates total communication cost for a federated round."""
        try:
            upload_per_client = self.estimate_upload(average_adapter)
            download_per_client = self.estimate_download(average_adapter)
            
            total_upload = upload_per_client * num_clients
            total_download = download_per_client * num_clients
            
            return {
                "total_transfer_bytes": total_upload + total_download,
                "estimated_latency_ms": self.estimate_latency(upload_per_client + download_per_client),
                "bandwidth_profile": self._profile
            }
        except Exception as e:
            raise CommunicationEstimationError(f"Failed to estimate round cost: {e}")
