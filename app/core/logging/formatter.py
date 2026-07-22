"""DriftAdapt Log Formatter Module.

Author: DriftAdapt Contributors
Purpose: Provides structured and human-readable string formats for log messages.
Future Integration: Invoked by console and file handlers inside DriftAdapt.
"""

from typing import Any


def log_formatter(record: Any) -> str:
    """Custom formatter for loguru records.

    Produces output matching:
    [2026-07-21 12:45:11] INFO [module] DeviceManager - CUDA detected
    Includes detailed metadata (function, line, thread, context) if available or debug active.
    """
    # Base pattern: timestamp, level
    fmt = "[{time:YYYY-MM-DD HH:mm:ss}] {level: <8} "

    # Module name (defaults to file path basename if not explicitly bound via extra context)
    module_name = record["extra"].get("module_name", record["name"])
    fmt += f"[{module_name}] "

    # Append function, line and thread context for DEBUG, TRACE, or ERROR levels
    level_name = record["level"].name
    if level_name in ("TRACE", "DEBUG", "ERROR", "CRITICAL"):
        thread_name = record["thread"].name
        fmt += f"({record['file'].name}:{record['function']}:{record['line']} on thread={thread_name}) - "
    else:
        fmt += "- "

    # Main message
    fmt += "{message}"

    # Optional payload/context dictionary
    context_data = record["extra"].get("context")
    if context_data:
        fmt += f" | Context: {context_data}"

    fmt += "\n{exception}"
    return fmt
