"""DriftAdapt Metrics Exporters Module.

Author: DriftAdapt Contributors
Purpose: Exports collected metrics to CSV and JSON files, defining telemetry interfaces.
Future Integration: Invoked by dashboard subscribers or end-of-experiment evaluations.
"""

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from app.core.metrics.exceptions import ExportError
from app.core.metrics.metric import Metric


class MetricExporter(ABC):
    """Abstract interface defining metrics file serialization routines."""

    @abstractmethod
    def export(self, metrics: List[Metric], output_path: Path) -> None:
        """Exports a list of metrics to a target output path."""
        pass


class CSVMetricExporter(MetricExporter):
    """Serializes collections of Metric records to structured CSV files."""

    def export(self, metrics: List[Metric], output_path: Path) -> None:
        if not metrics:
            return

        try:
            # Ensure target parent directories exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(
                    [
                        "name",
                        "value",
                        "timestamp",
                        "module",
                        "step",
                        "round",
                        "client_id",
                        "experiment_id",
                        "metadata",
                    ]
                )

                # Write records
                for m in metrics:
                    writer.writerow(
                        [
                            m.name,
                            str(m.value),
                            m.timestamp,
                            m.module,
                            m.step if m.step is not None else "",
                            m.round if m.round is not None else "",
                            m.client_id if m.client_id is not None else "",
                            m.experiment_id if m.experiment_id is not None else "",
                            json.dumps(m.metadata),
                        ]
                    )
        except Exception as e:
            raise ExportError(f"Failed to export metrics to CSV at {output_path}: {e}") from e


class JSONMetricExporter(MetricExporter):
    """Serializes collections of Metric records to standard JSON lists."""

    def export(self, metrics: List[Metric], output_path: Path) -> None:
        if not metrics:
            return

        try:
            # Ensure target parent directories exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Dump pydantic objects directly
            data = [m.model_dump() for m in metrics]

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            raise ExportError(f"Failed to export metrics to JSON at {output_path}: {e}") from e


# Placeholders for future third-party integrations
class TensorBoardExporter(MetricExporter):
    """Placeholder interface to export records to TensorBoard event files."""

    def export(self, metrics: List[Metric], output_path: Path) -> None:
        raise NotImplementedError("TensorBoard export is reserved for Module 10.")


class WandBExporter(MetricExporter):
    """Placeholder interface to publish records to Weights & Biases."""

    def export(self, metrics: List[Metric], output_path: Path) -> None:
        raise NotImplementedError("WandB export is reserved for Module 10.")


class MLFlowExporter(MetricExporter):
    """Placeholder interface to publish records to MLFlow tracking servers."""

    def export(self, metrics: List[Metric], output_path: Path) -> None:
        raise NotImplementedError("MLFlow export is reserved for Module 10.")
