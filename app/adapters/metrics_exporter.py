"""DriftAdapt Metrics Exporter.

Author: DriftAdapt Contributors
Purpose: Exports metrics to standard data formats.
"""

import csv
import json
from pathlib import Path

from app.adapters.metrics_exceptions import ExportFailed
from app.adapters.metrics_registry import MetricsRegistry
from app.core.logging.logger_factory import LoggerFactory


class MetricsExporter:
    """Exports metrics to JSON and CSV formats."""
    
    def __init__(self, registry: MetricsRegistry, export_dir: Path) -> None:
        self._registry = registry
        self._export_dir = export_dir
        self._logger = LoggerFactory.get_logger("MetricsExporter")
        self._export_dir.mkdir(parents=True, exist_ok=True)
        
    def export_json(self, filename: str = "metrics_export.json") -> Path:
        """Exports all metrics to a structured JSON file."""
        try:
            path = self._export_dir / filename
            data = {
                "adapters": [m.model_dump() for m in self._registry.get_adapter_history()],
                "communication": [m.model_dump() for m in self._registry.get_communication_history()],
                "performance": [m.model_dump() for m in self._registry.get_performance_history()],
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            self._logger.info(f"Exported metrics to {path}")
            return path
        except Exception as e:
            raise ExportFailed(f"Failed to export JSON: {e}")
            
    def export_csv(self, filename: str = "adapter_metrics.csv") -> Path:
        """Exports adapter metrics specifically to a flat CSV file."""
        try:
            path = self._export_dir / filename
            history = self._registry.get_adapter_history()
            if not history:
                with open(path, "w") as f:
                    pass
                return path
                
            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(history[0].model_fields.keys()))
                writer.writeheader()
                for m in history:
                    writer.writerow(m.model_dump())
            self._logger.info(f"Exported adapter metrics to {path}")
            return path
        except Exception as e:
            raise ExportFailed(f"Failed to export CSV: {e}")
