"""DriftAdapt Personalization LoRA Schemas.

Author: DriftAdapt Contributors
Purpose: Strictly validates typing, ranges, and structures for LoRA configuration parameters using Pydantic.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class AdapterConfiguration(BaseModel):
    """Metadata describing the PEFT adapter."""
    name: str = Field(..., description="Unique name identifier for the adapter.")
    version: str = Field(..., description="Adapter version string (e.g. '1.0').")
    description: str = Field(default="", description="Detailed description of the adapter.")
    author: str = Field(default="DriftAdapt", description="Creator or organization name.")
    organization: str = Field(default="Research", description="Organization name.")
    creation_timestamp: Optional[str] = Field(default=None, description="ISO timestamp of creation.")
    uuid: Optional[str] = Field(default=None, description="Unique UUID for the adapter instance.")
    tags: List[str] = Field(default_factory=list, description="Categorical tags for filtering.")


class LoRAHyperparameters(BaseModel):
    """Core LoRA algorithm hyperparameters."""
    rank: int = Field(default=16, description="Rank of the update matrices (r).")
    alpha: float = Field(default=32.0, description="LoRA scaling factor (alpha).")
    dropout: float = Field(default=0.05, description="Dropout probability for LoRA layers.")
    bias: Literal["none", "all", "lora_only"] = Field(default="none", description="Bias training strategy.")
    task_type: Literal["CAUSAL_LM", "SEQ_2_SEQ_LM", "TOKEN_CLS", "SEQ_CLS"] = Field(
        default="CAUSAL_LM", description="PEFT task type."
    )
    inference_mode: bool = Field(default=False, description="Whether to load adapter in inference mode.")
    fan_in_fan_out: bool = Field(default=False, description="Set True if the layer replaces Conv1D with Linear.")
    modules_to_save: List[str] = Field(
        default_factory=list, description="Modules apart from LoRA layers to be set as trainable and saved."
    )
    init_lora_weights: Literal[True, False, "gaussian", "loftq"] = Field(
        default=True, description="Initialization strategy for LoRA weights."
    )


class TargetModuleConfiguration(BaseModel):
    """Configuration for specifying which transformer layers to target with LoRA."""
    modules: List[str] = Field(
        default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        description="List of target module names."
    )


class PrecisionConfiguration(BaseModel):
    """Precision and dtype settings for adapter training and inference."""
    dtype: Literal["float32", "float16", "bfloat16"] = Field(
        default="bfloat16", description="Compute data type for the adapter."
    )
    mixed_precision: bool = Field(default=True, description="Enable automatic mixed precision (AMP).")
    gradient_checkpointing: bool = Field(default=True, description="Enable gradient checkpointing for memory efficiency.")
    autocast: bool = Field(default=True, description="Enable torch.autocast during forward passes.")


class StorageConfiguration(BaseModel):
    """File system paths for persisting adapters and checkpoints."""
    adapter_directory: str = Field(default="./models/adapters", description="Directory to save final adapters.")
    checkpoint_directory: str = Field(default="./models/checkpoints", description="Directory to save training checkpoints.")
    export_directory: str = Field(default="./models/exports", description="Directory for merged model exports.")
    temporary_directory: str = Field(default="/tmp/driftadapt", description="Temporary scratch space.")
    cache_directory: str = Field(default="./models/cache", description="General cache directory.")


class TrainingConfiguration(BaseModel):
    """Training hyperparameter configurations for fine-tuning the adapter."""
    learning_rate: float = Field(default=2e-4, description="Peak learning rate.")
    batch_size: int = Field(default=4, description="Per-device training batch size.")
    epochs: int = Field(default=3, description="Total number of training epochs.")
    gradient_accumulation_steps: int = Field(default=4, description="Steps to accumulate gradients before update.")
    optimizer: Literal["adamw_torch", "adamw_8bit", "paged_adamw_8bit", "sgd"] = Field(
        default="adamw_torch", description="Optimizer to use."
    )
    scheduler: Literal["linear", "cosine", "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"] = Field(
        default="cosine", description="Learning rate schedule."
    )
    warmup_ratio: float = Field(default=0.03, description="Ratio of total steps for learning rate warmup.")
    weight_decay: float = Field(default=0.001, description="Weight decay applied to parameters.")
    gradient_clipping: bool = Field(default=True, description="Enable gradient norm clipping.")
    max_grad_norm: float = Field(default=1.0, description="Maximum gradient norm threshold.")
    logging_steps: int = Field(default=10, description="Frequency of logging training metrics.")
    evaluation_steps: int = Field(default=50, description="Frequency of evaluating on validation set.")


class CheckpointConfiguration(BaseModel):
    """Checkpointing behavior and state preservation settings."""
    save_every: int = Field(default=100, description="Save a checkpoint every N steps.")
    keep_last: int = Field(default=3, description="Maximum number of recent checkpoints to retain.")
    save_optimizer: bool = Field(default=True, description="Include optimizer states in checkpoint.")
    save_scheduler: bool = Field(default=True, description="Include scheduler states in checkpoint.")
    resume_training: bool = Field(default=False, description="Automatically resume from the latest checkpoint if found.")
    export_format: Literal["safetensors", "pt", "bin"] = Field(default="safetensors", description="State dict export format.")


class LoggingConfiguration(BaseModel):
    """Verbosity and telemetry configuration for Personalization workflows."""
    verbose: bool = Field(default=True, description="Enable verbose logging.")
    log_parameter_count: bool = Field(default=True, description="Log trainable vs frozen parameter counts.")
    log_adapter_creation: bool = Field(default=True, description="Log adapter instantiation details.")
    log_serialization: bool = Field(default=True, description="Log serialization events to disk.")
    log_validation: bool = Field(default=True, description="Log schema validation errors/warnings.")


class ValidationConfiguration(BaseModel):
    """Toggles for strict validation checks during configuration parsing."""
    verify_target_modules: bool = Field(default=True, description="Check for duplicates or empty target modules.")
    verify_parameter_count: bool = Field(default=True, description="Assert parameters before training.")
    verify_adapter_metadata: bool = Field(default=True, description="Ensure adapter naming is compliant.")
    verify_storage_paths: bool = Field(default=True, description="Check if directories exist or can be created.")
    verify_precision: bool = Field(default=True, description="Assert dtype compatibility with hardware.")
    verify_task_type: bool = Field(default=True, description="Assert supported task types for PEFT.")


class PersonalizationConfiguration(BaseModel):
    """The root configuration object aggregating all personalization parameters."""
    adapter: AdapterConfiguration = Field(default_factory=lambda: AdapterConfiguration(**{}))
    lora: LoRAHyperparameters = Field(default_factory=lambda: LoRAHyperparameters(**{}))
    target_modules: TargetModuleConfiguration = Field(default_factory=lambda: TargetModuleConfiguration(**{}))
    precision: PrecisionConfiguration = Field(default_factory=lambda: PrecisionConfiguration(**{}))
    storage: StorageConfiguration = Field(default_factory=lambda: StorageConfiguration(**{}))
    training: TrainingConfiguration = Field(default_factory=lambda: TrainingConfiguration(**{}))
    checkpoint: CheckpointConfiguration = Field(default_factory=lambda: CheckpointConfiguration(**{}))
    logging: LoggingConfiguration = Field(default_factory=lambda: LoggingConfiguration(**{}))
    validation: ValidationConfiguration = Field(default_factory=lambda: ValidationConfiguration(**{}))
