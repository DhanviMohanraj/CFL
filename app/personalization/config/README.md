# DriftAdapt LoRA Configuration Manager (Module 2.1)

## Overview
The LoRA Configuration Manager is the centralized source of truth for all PEFT (Parameter-Efficient Fine-Tuning) and Personalization settings in the DriftAdapt platform. It handles the loading, deep merging, robust validation, and serialization of LoRA hyperparameters, target modules, precision settings, and training parameters.

This module acts purely as a configuration backbone. It does NOT implement PEFT injection, model training, or inference—those are responsibilities of downstream modules (e.g. Module 2.2 PEFT Integration Layer).

## Configuration Hierarchy

Configurations are merged in the following priority (highest to lowest):
1. **Runtime Overrides:** Programmatic dictionaries passed at runtime.
2. **Environment Variables:** Values prefixed with `DRIFTADAPT__LORA__`.
3. **YAML Configuration:** User-provided `.yaml` configuration file.
4. **JSON Configuration:** User-provided `.json` configuration file.
5. **Default Configuration:** Hardcoded safe defaults (`lora_defaults.py`).

## Core Components
- **`LoRAConfigurationManager`**: The Singleton entry point to load, access, and serialize configurations.
- **`PersonalizationConfiguration`**: The root Pydantic v2 schema encapsulating all settings.
- **`LoRAConfigurationLoader`**: Handles file I/O and deep dictionary merging.
- **`LoRAConfigurationValidator`**: Enforces strict mathematical and logical boundaries (e.g., positive rank, valid dtypes, unique target modules) before Pydantic instantiation.

## Validation Rules
- **Rank (`r`)**: Must be > 0.
- **Alpha**: Must be > 0.
- **Dropout**: Must be bounded [0.0, 1.0].
- **Target Modules**: Cannot be empty; duplicates are rejected.
- **Task Type**: Must be one of `CAUSAL_LM`, `SEQ_2_SEQ_LM`, `TOKEN_CLS`, `SEQ_CLS`.
- **Precision (`dtype`)**: Must be one of `float32`, `float16`, `bfloat16`.
- **Training**: Learning rate > 0, batch size > 0, epochs > 0.

## Developer Guide & Integration

Future modules should access personalization settings using the Singleton manager:

```python
from app.personalization.config import LoRAConfigurationManager

# 1. Get Manager Instance
config_manager = LoRAConfigurationManager()

# 2. Optionally load from specific paths (defaults are used otherwise)
config_manager.configure_paths(yaml_path="configs/lora.yaml")

# 3. Apply any dynamic runtime overrides if needed
config_manager.apply_overrides({"lora": {"rank": 32}})

# 4. Load the strongly-typed PersonalizationConfiguration object
config = config_manager.load()

# 5. Access values safely
print(f"Rank: {config.lora.rank}")
print(f"Target Modules: {config.target_modules.modules}")
print(f"Learning Rate: {config.training.learning_rate}")
```

## Extension Points
To add new configuration sections:
1. Define a new Pydantic schema in `lora_schema.py`.
2. Add the schema to the root `PersonalizationConfiguration` class.
3. Provide safe default values in `lora_defaults.py`.
4. Add any custom logic rules to `LoRAConfigurationValidator`.
