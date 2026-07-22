# DriftAdapt PEFT Integration Layer (Module 2.2)

## Overview
The **PEFT Integration Layer** acts as the crucial bridge between the frozen Foundation Model (Module 1) and the LoRA Configuration Manager (Module 2.1). It safely wraps the heavy foundational base model with trainable, lightweight LoRA (Low-Rank Adaptation) layers using Hugging Face's `peft` library, without altering the base model's immutability.

This module guarantees strict adherence to validation rules, reporting metrics, and providing a clean API for Module 2.3 (Adapter Manager) and Module 2.4 (Personalization Loop) to train on.

## Core Responsibilities
- **Injection:** Takes the frozen base model and applies LoRA `peft.get_peft_model`.
- **Validation:** 
  - Asserts that all non-adapter parameters retain `requires_grad=False`.
  - Asserts the configured `target_modules` actually exist in the base model architecture.
  - Verifies the ratio of trainable parameters.
- **Metrics:** Synchronizes adapter injection time, trainable parameter counts, and total parameters with the `MetricsBus`.

## Architecture & Integration Flow
```text
[Module 1 (ModelManager)] ----> [Base Foundation Model (Frozen)]
                                               |
                                               v
[Module 2.1 (Config)] --------> [Module 2.2 (PEFT Integration)] ----> [PeftModel (Trainable)]
                                               |
                                               v
                                [Adapter Metadata & Validation]
```

## Developer Guide

### Retrieving the Wrapped Model
Downstream modules (like training loops) only need to interact with the `PEFTManager` singleton.

```python
from app.personalization.peft import PEFTManager

# 1. Instantiate the singleton facade
peft_mgr = PEFTManager()

# 2. Get the injected peft model (automatically initialized if needed)
wrapped_model = peft_mgr.get_model()

# 3. Retrieve metadata regarding trainable parameters
metadata = peft_mgr.get_metadata()
print(f"Trainable Parameters: {metadata.trainable_parameters}")
print(f"Trainable Ratio: {metadata.trainable_ratio:.4%}")
```

### Components
- **`PEFTManager`**: Singleton orchestrator. Coordinates ModelManager and LoRA config.
- **`InjectionEngine`**: Internal class executing the Hugging Face PEFT wrapping.
- **`AdapterFactory`**: Internal class building the `peft.LoraConfig` from our Pydantic schemas.
- **`AdapterValidator` & `ParameterInspector`**: Security and integrity guardrails.

## Exception Hierarchy
- `PEFTIntegrationError` (Base)
  - `AdapterInjectionError` (Wraps `peft` internal errors)
  - `TargetModuleNotFoundError` (Typo in config target modules)
  - `AdapterValidationError` (Trainable parameter check failed)
  - `FrozenModelViolationError` (Base model weights became trainable!)
