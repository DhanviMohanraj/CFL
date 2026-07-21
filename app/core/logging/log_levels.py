"""DriftAdapt Log Levels Module.

Author: DriftAdapt Contributors
Purpose: Defines severity metrics and custom logging levels (e.g. SUCCESS, TRACE).
Future Integration: Exposes level maps to handlers, logger factory, and config manager.
"""

from typing import Dict

# Mapping standard level names to severity integers
LOG_SEVERITIES: Dict[str, int] = {
    "TRACE": 5,
    "DEBUG": 10,
    "INFO": 20,
    "SUCCESS": 25,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


def get_level_severity(level_name: str) -> int:
    """Returns severity score for a level name. Default is INFO (20) if unknown."""
    return LOG_SEVERITIES.get(level_name.upper().strip(), 20)
