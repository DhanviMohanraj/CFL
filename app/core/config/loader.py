"""DriftAdapt Configuration Loader Module.

Author: DriftAdapt Contributors
Purpose: Resolves project roots, loads YAML configurations, and applies environment variables.
Future Integration: Exposes parsing utilities to ConfigManager and ConfigFactory.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

from app.core.config.defaults import DEFAULT_APP_CONFIG
from app.core.config.exceptions import (
    ConfigurationError,
    FileNotFoundConfiguration,
    InvalidConfiguration,
)


def get_project_root() -> Path:
    """Dynamically resolves the project root directory.

    Guarantees cross-platform resolution on Windows, Linux, and macOS.
    """
    # Assuming this file resides in project_root/app/core/config/loader.py
    current_path = Path(__file__).resolve()
    return current_path.parent.parent.parent.parent


def load_env_file() -> None:
    """Loads environment variables from local .env file if present in the project root."""
    root = get_project_root()
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # Fallback to general environment load
        load_dotenv()


def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merges a source dictionary into a target dictionary.

    Returns a new merged dictionary.
    """
    result = target.copy()
    for key, value in source.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Loads a single YAML configuration file.

    Raises custom exceptions for file missing and formatting errors.
    """
    if not file_path.exists():
        raise FileNotFoundConfiguration(
            f"Configuration file not found at: {file_path}"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except yaml.YAMLError as e:
        raise InvalidConfiguration(
            f"YAML syntax error in file {file_path.name}: {e}"
        ) from e
    except Exception as e:
        raise ConfigurationError(
            f"Failed to read configuration file {file_path.name}: {e}"
        ) from e


def apply_env_overrides(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Applies environment variable overrides to the configuration dictionary.

    Supports:
    1. Direct environment mappings:
       - MODEL_NAME -> model.foundation_model
       - DEVICE -> system.device
       - DEBUG -> system.debug
       - LOG_LEVEL -> logging.log_level
       - OUTPUT_DIR -> evaluation.output_dir
    2. Dynamic scoped format: DRIFTADAPT_<SECTION>__<KEY>
       e.g., DRIFTADAPT_TRAINING__LEARNING_RATE=1e-5
    """
    # Create a copy to prevent mutation of the input dict
    result = deep_merge({}, config_dict)

    # 1. Direct standard overrides
    model_name = os.getenv("MODEL_NAME")
    if model_name:
        result.setdefault("model", {})["foundation_model"] = model_name
        result.setdefault("model", {})["tokenizer"] = model_name

    device = os.getenv("DEVICE")
    if device:
        result.setdefault("system", {})["device"] = device

    debug_val = os.getenv("DEBUG")
    if debug_val is not None:
        result.setdefault("system", {})["debug"] = debug_val.lower() in ("true", "1", "yes")

    log_level = os.getenv("LOG_LEVEL")
    if log_level:
        result.setdefault("logging", {})["log_level"] = log_level.upper()

    output_dir = os.getenv("OUTPUT_DIR")
    if output_dir:
        result.setdefault("evaluation", {})["output_dir"] = output_dir

    # 2. Dynamic environment variable overrides
    # Syntax: DRIFTADAPT_<SECTION>__<KEY>=value
    for env_name, env_val in os.environ.items():
        if env_name.startswith("DRIFTADAPT_") and "__" in env_name:
            # e.g., DRIFTADAPT_TRAINING__LEARNING_RATE
            raw_payload = env_name[len("DRIFTADAPT_") :]
            section, key = raw_payload.split("__", 1)
            section = section.lower()
            key = key.lower()

            if section in DEFAULT_APP_CONFIG:
                # Convert type if key exists in default template
                default_val = DEFAULT_APP_CONFIG[section].get(key)
                typed_val: Any = env_val

                if default_val is not None:
                    if isinstance(default_val, bool):
                        typed_val = env_val.lower() in ("true", "1", "yes")
                    elif isinstance(default_val, int):
                        typed_val = int(env_val)
                    elif isinstance(default_val, float):
                        typed_val = float(env_val)
                    elif isinstance(default_val, list):
                        typed_val = [item.strip() for item in env_val.split(",")]

                result.setdefault(section, {})[key] = typed_val

    return result


def load_raw_configurations(configs_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Loads all yaml configurations from the targets directory and merges them.

    Applies default templates for missing files/sections.
    """
    if configs_dir is None:
        configs_dir = get_project_root() / "configs"

    # Seed the merged result with default profiles
    merged_config = deep_merge({}, DEFAULT_APP_CONFIG)

    # List of configuration files to load
    config_mappings = {
        "system": configs_dir / "system.yaml",
        "model": configs_dir / "model.yaml",
        "lora": configs_dir / "lora.yaml",
        "training": configs_dir / "training.yaml",
        "federated": configs_dir / "federated.yaml",
        "dataset": configs_dir / "dataset.yaml",
        "drift": configs_dir / "drift.yaml",
        "evaluation": configs_dir / "evaluation.yaml",
        "logging": configs_dir / "logging.yaml",
        "experiment": configs_dir / "experiment.yaml",
    }

    # Load and merge each file
    for section, file_path in config_mappings.items():
        try:
            yaml_content = load_yaml(file_path)
            merged_config[section] = deep_merge(merged_config.get(section, {}), yaml_content)
        except FileNotFoundConfiguration:
            # Silently fallback to defaults if file is missing (warnings can be added later)
            pass

    return merged_config
