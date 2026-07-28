"""DriftAdapt Timeout Manager.

Author: DriftAdapt Contributors
"""

from app.core.logging.logger_factory import LoggerFactory
from app.federated.coordinator.coordinator_exceptions import SynchronizationTimeout
from app.federated.coordinator.coordinator_metrics import CoordinatorMetrics


class TimeoutManager:
    """Detects timeouts and triggers appropriate actions."""
    
    def __init__(self, metrics: CoordinatorMetrics, upload_timeout: float = 300.0) -> None:
        self._logger = LoggerFactory.get_logger("TimeoutManager")
        self._metrics = metrics
        self._upload_timeout = upload_timeout
        
    def handle_upload_timeout(self, round_id: str, client_id: str) -> None:
        """Handles a specific client upload timeout."""
        self._logger.warning(f"Client {client_id} timed out uploading for round {round_id}.")
        self._metrics.publish_timeout("upload")
        
    def check_synchronization_timeout(self, elapsed: float, max_timeout: float) -> None:
        """Checks if global sync has timed out."""
        if elapsed > max_timeout:
            self._logger.error(f"Global synchronization timeout exceeded: {elapsed}s > {max_timeout}s")
            self._metrics.publish_timeout("synchronization")
            raise SynchronizationTimeout("Global synchronization timed out.")
