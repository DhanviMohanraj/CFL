"""DriftAdapt Adaptation Priority.

Author: DriftAdapt Contributors
"""

from enum import Enum


class PriorityLevel(str, Enum):
    """Defines adaptation priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UrgencyLevel(str, Enum):
    """Defines adaptation urgency levels."""
    DEFERRED = "DEFERRED"
    MANUAL = "MANUAL"
    NEXT_ROUND = "NEXT_ROUND"
    IMMEDIATE = "IMMEDIATE"
