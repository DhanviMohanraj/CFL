"""DriftAdapt Metric Types Module.

Author: DriftAdapt Contributors
Purpose: Defines enum categories representing telemetry and metrics targets.
Future Integration: Enforced by the MetricRegistry to validate published structures.
"""

from enum import Enum


class MetricType(str, Enum):
    """Categorized types of metrics collected in the DriftAdapt system."""

    TRAINING = "training"
    VALIDATION = "validation"
    SYSTEM = "system"
    COMMUNICATION = "communication"
    DRIFT = "drift"
    FEDERATION = "federation"
    PERSONALIZATION = "personalization"
    MEMORY = "memory"
    GPU = "gpu"
    CPU = "cpu"
    LATENCY = "latency"
    LOSS = "loss"
    ACCURACY = "accuracy"
    CUSTOM = "custom"
