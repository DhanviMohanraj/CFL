"""DriftAdapt Adapter Registry Storage Module.

Author: DriftAdapt Contributors
Purpose: Handles file IO operations for the Adapter Registry persistence.
"""

import json
from pathlib import Path
from typing import Any, Dict


def read_json_file(file_path: Path) -> Dict[str, Any]:
    """Reads a JSON file safely.
    
    Args:
        file_path: Path to the JSON file.
        
    Returns:
        The parsed JSON content as a dictionary.
        
    Raises:
        Exception: If the file cannot be read or parsed.
    """
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(file_path: Path, data: Dict[str, Any]) -> None:
    """Writes a dictionary to a JSON file safely.
    
    Creates parent directories if they don't exist.
    
    Args:
        file_path: Path to the JSON file.
        data: The dictionary to write.
        
    Raises:
        Exception: If the file cannot be written.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
