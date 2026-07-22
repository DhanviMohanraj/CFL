"""DriftAdapt Model Information Report Module.

Author: DriftAdapt Contributors
Purpose: Provides structured report object supporting text summaries, dict output, and metrics conversion.
Future Integration: Queried for dashboards, logs, and experiment tracking.
"""

from typing import Any, Dict

from app.models.foundation.model_metadata import ModelMetadata


class ModelInfo:
    """Encapsulates foundation model information with multiple export representations."""

    def __init__(self, metadata: ModelMetadata) -> None:
        """Initializes ModelInfo wrapper around metadata."""
        self._metadata = metadata

    @property
    def metadata(self) -> ModelMetadata:
        """Returns the underlying ModelMetadata model."""
        return self._metadata

    def to_dict(self) -> Dict[str, Any]:
        """Converts model metadata into a standard Python dictionary."""
        return self._metadata.model_dump()

    def to_metrics_dict(self) -> Dict[str, Any]:
        """Flattens numerical and categorical parameters into telemetry metrics format."""
        return {
            "model.parameter_count": self._metadata.parameter_count,
            "model.trainable_parameters": self._metadata.trainable_parameters,
            "model.vocab_size": self._metadata.vocab_size,
            "model.context_length": self._metadata.context_length,
            "model.hidden_size": self._metadata.hidden_size,
            "model.memory_footprint_mb": self._metadata.memory_footprint_mb,
            "model.load_time_seconds": self._metadata.load_time_seconds,
            "model.disk_size_mb": self._metadata.disk_size_mb,
            "model.is_frozen": int(self._metadata.is_frozen),
        }

    def get_summary_report(self) -> str:
        """Generates a human-readable text summary of the foundation model."""
        meta = self._metadata
        lines = [
            "=" * 60,
            f"DRIFTADAPT FOUNDATION MODEL SUMMARY - {meta.model_name}",
            "=" * 60,
            f"Architecture:         {meta.architecture}",
            f"Total Parameters:     {meta.parameter_count:,} ({meta.parameter_count / 1e9:.2f}B)",
            f"Trainable Parameters: {meta.trainable_parameters:,}",
            f"Parameters Frozen:    {meta.is_frozen}",
            f"Tokenizer:            {meta.tokenizer_name}",
            f"Vocabulary Size:      {meta.vocab_size:,}",
            f"Context Length:       {meta.context_length:,}",
            f"Hidden Dimension:     {meta.hidden_size:,}",
            "-" * 60,
            "Runtime Execution Specifications:",
            f"  Target Device:      {meta.device}",
            f"  Quantization Mode:  {meta.quantization_mode}",
            f"  Precision Dtype:    {meta.precision}",
            f"  Memory Footprint:   {meta.memory_footprint_mb:.2f} MB",
            f"  Load Time:          {meta.load_time_seconds:.2f} seconds",
            f"  Disk Size:          {meta.disk_size_mb:.2f} MB",
            f"  Checkpoint Location: {meta.checkpoint_location or 'In-Memory'}",
            "=" * 60,
        ]
        return "\n".join(lines)
