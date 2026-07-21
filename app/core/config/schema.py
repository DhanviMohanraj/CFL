"""DriftAdapt Pydantic Schemas for Configuration.

Author: DriftAdapt Contributors
Purpose: Strictly validates typing, ranges, and structures of DriftAdapt configuration modules.
Future Integration: Loaded and validated by loader and config manager modules.
"""

from typing import List, Dict, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class SystemConfig(BaseModel):
    """Configuration for system paths, random seeds, and resources."""

    project_name: str = Field(
        default="DriftAdapt",
        description="The primary name of the project."
    )
    project_version: str = Field(
        default="0.1.0",
        description="Version version format descriptor."
    )
    random_seed: int = Field(
        default=42,
        description="Global seed for training, splits, and initialization reproducibility."
    )
    device: Literal["cuda", "cpu", "mps"] = Field(
        default="cuda",
        description="Target acceleration hardware to initialize models on."
    )
    logs_dir: str = Field(
        default="./logs",
        description="Filsystem location to store log files."
    )
    experiments_dir: str = Field(
        default="./experiments",
        description="Filsystem location to export trial run parameters."
    )
    checkpoints_dir: str = Field(
        default="./checkpoints",
        description="Filsystem cache location for model weights."
    )
    datasets_dir: str = Field(
        default="./datasets",
        description="Filsystem container for datasets."
    )
    metrics_dir: str = Field(
        default="./metrics",
        description="Filsystem container for metrics files."
    )

    num_workers: int = Field(
        default=4,
        description="Total processes dedicated to loading PyTorch batches."
    )
    debug: bool = Field(
        default=False,
        description="If True, overrides epochs/batches to run in validation sandbox."
    )

    @field_validator("random_seed")
    @classmethod
    def validate_seed(cls, val: int) -> int:
        if val < 0:
            raise ValueError("Random seed must be a non-negative integer.")
        return val

    @field_validator("num_workers")
    @classmethod
    def validate_workers(cls, val: int) -> int:
        if val < 0:
            raise ValueError("Number of workers cannot be negative.")
        return val


class ModelConfig(BaseModel):
    """Configuration parameters for the Base Foundation Model."""

    foundation_model: str = Field(
        default="meta-llama/Meta-Llama-3-8B-Instruct",
        description="Hugging Face repo or local path of base Foundation Model."
    )
    tokenizer: str = Field(
        default="meta-llama/Meta-Llama-3-8B-Instruct",
        description="Hugging Face repo or local path of tokenizer."
    )
    max_seq_length: int = Field(
        default=512,
        description="Maximum tokens allowed per context evaluation step."
    )
    context_window: int = Field(
        default=2048,
        description="Base window size initialized by the model."
    )
    quantization: Literal["4bit", "8bit", "none"] = Field(
        default="4bit",
        description="Model weight bitsandbytes quantization compression state."
    )
    precision: Literal["float16", "bfloat16", "float32"] = Field(
        default="bfloat16",
        description="Optimizer tensor float precision settings."
    )
    cache_dir: str = Field(
        default="./checkpoints/hf_cache",
        description="Local path to download/retrieve Hugging Face files."
    )
    use_cache: bool = Field(
        default=True,
        description="If true, reuse loaded weights from local cache."
    )

    @field_validator("max_seq_length", "context_window")
    @classmethod
    def validate_lengths(cls, val: int) -> int:
        if val <= 0:
            raise ValueError("Sequence and context sizes must be greater than zero.")
        return val


class LoRAConfig(BaseModel):
    """Configuration parameters for Low-Rank Adapters (PEFT)."""

    r: int = Field(
        default=8,
        description="Rank dimension of LoRA updates."
    )
    lora_alpha: int = Field(
        default=16,
        description="Scaling factor for adapter weights."
    )
    lora_dropout: float = Field(
        default=0.05,
        description="Dropout rate within LoRA layers to prevent overfitting."
    )
    bias: Literal["none", "all", "lora_only"] = Field(
        default="none",
        description="Specify if bias parameters should be trained."
    )
    target_modules: List[str] = Field(
        default_factory=lambda: ["q_proj", "v_proj", "k_proj", "o_proj"],
        description="Specific model attention projection layers to attach adapters to."
    )
    adapters_dir: str = Field(
        default="./checkpoints/adapters",
        description="Path to save or retrieve local model adapters."
    )
    version: str = Field(
        default="v1.0",
        description="Local tag detailing fine-tuned version tracker."
    )

    @field_validator("r", "lora_alpha")
    @classmethod
    def validate_positive_ints(cls, val: int) -> int:
        if val <= 0:
            raise ValueError("LoRA r and alpha must be positive integers.")
        return val

    @field_validator("lora_dropout")
    @classmethod
    def validate_dropout(cls, val: float) -> float:
        if not (0.0 <= val <= 1.0):
            raise ValueError("LoRA dropout rate must lie between 0.0 and 1.0 inclusive.")
        return val


class TrainingConfig(BaseModel):
    """Configuration for local optimizer and training parameters."""

    batch_size: int = Field(
        default=8,
        description="Local mini-batch training size."
    )
    epochs: int = Field(
        default=3,
        description="Epoch count for local training sweeps."
    )
    optimizer: str = Field(
        default="adamw_torch",
        description="Optimizer name (e.g. adamw_torch, sgd)."
    )
    learning_rate: float = Field(
        default=2e-4,
        description="Initial optimizer learning rate."
    )
    scheduler: str = Field(
        default="cosine",
        description="Learning rate adjustment scheduler."
    )
    gradient_accumulation_steps: int = Field(
        default=4,
        description="Number of batches to accumulate gradients before taking step."
    )
    mixed_precision: Literal["fp16", "bf16", "none"] = Field(
        default="bf16",
        description="Autocast precision setting (float16, bfloat16, none)."
    )
    weight_decay: float = Field(
        default=0.01,
        description="Weight decay rate for regularization."
    )
    max_grad_norm: float = Field(
        default=1.0,
        description="Max grad value clip to prevent exploding gradients."
    )

    @field_validator("batch_size", "epochs", "gradient_accumulation_steps")
    @classmethod
    def validate_positive_ints(cls, val: int) -> int:
        if val <= 0:
            raise ValueError("Batch size, epochs, and accumulation steps must be positive.")
        return val

    @field_validator("learning_rate")
    @classmethod
    def validate_learning_rate(cls, val: float) -> float:
        if val <= 0.0:
            raise ValueError("Learning rate must be strictly positive.")
        return val

    @field_validator("weight_decay", "max_grad_norm")
    @classmethod
    def validate_non_negative_floats(cls, val: float) -> float:
        if val < 0.0:
            raise ValueError("Regularization parameters cannot be negative.")
        return val


class FederatedConfig(BaseModel):
    """Configuration governing federated clients and aggregations."""

    num_clients: int = Field(
        default=10,
        description="Simulated or real count of edge client instances."
    )
    participation_rate: float = Field(
        default=0.8,
        description="Client percentage activated per round."
    )
    algorithm: Literal["fedavg", "fedprox", "fedopt"] = Field(
        default="fedavg",
        description="Weight combining algorithm."
    )
    num_rounds: int = Field(
        default=50,
        description="Max rounds to execute federated sync."
    )
    local_epochs: int = Field(
        default=3,
        description="Epoch training runs performed client-side locally."
    )
    client_timeout: float = Field(
        default=30.0,
        description="Client connection timeout in seconds."
    )
    communication_frequency: int = Field(
        default=1,
        description="Communication sync interval (rounds count)."
    )

    @field_validator("num_clients", "num_rounds", "local_epochs", "communication_frequency")
    @classmethod
    def validate_positive_ints(cls, val: int) -> int:
        if val <= 0:
            raise ValueError("Clients, rounds, epochs, and communication rates must be positive.")
        return val

    @field_validator("participation_rate")
    @classmethod
    def validate_participation(cls, val: float) -> float:
        if not (0.0 < val <= 1.0):
            raise ValueError("Participation rate must be strictly between 0.0 and 1.0 (inclusive).")
        return val

    @field_validator("client_timeout")
    @classmethod
    def validate_timeout(cls, val: float) -> float:
        if val < 0.0:
            raise ValueError("Timeout cannot be negative.")
        return val


class SplitConfig(BaseModel):
    """Split ratios configuration."""

    train: float = Field(default=0.7, description="Train split ratio.")
    val: float = Field(default=0.1, description="Val split ratio.")
    test: float = Field(default=0.2, description="Test split ratio.")

    @model_validator(mode="after")
    def validate_sum(self) -> "SplitConfig":
        total = self.train + self.val + self.test
        if not (0.99 <= total <= 1.01):
            raise ValueError("Train, val, and test ratios must sum up to 1.0.")
        return self


class DatasetConfig(BaseModel):
    """Configuration detailing inputs, client partitions, and online streams."""

    dataset_name: str = Field(
        default="MIMIC-IV-Advisory",
        description="Target dataset registration name."
    )
    split_ratios: SplitConfig = Field(
        default_factory=SplitConfig,
        description="Proportions dedicated to training, validation, and test sets."
    )
    clinic_partitions: int = Field(
        default=10,
        description="Number of non-IID target clinics partitions to map clients to."
    )
    season_partitions: List[str] = Field(
        default_factory=lambda: ["summer", "rainy", "winter"],
        description="Available data shift blocks representing seasons."
    )
    shuffle: bool = Field(
        default=True,
        description="If True, shuffle local client datasets."
    )
    stream_batch_size: int = Field(
        default=32,
        description="Evaluation feed batch sizes."
    )

    @field_validator("clinic_partitions", "stream_batch_size")
    @classmethod
    def validate_positive_ints(cls, val: int) -> int:
        if val <= 0:
            raise ValueError("Partitions and stream batch sizes must be positive.")
        return val


class DriftConfig(BaseModel):
    """Configuration parameters for monitoring distribution drifts."""

    drift_detector: Literal["adwin", "kswin", "page_hinkley"] = Field(
        default="adwin",
        description="Target detector backend wrapper."
    )
    window_size: int = Field(
        default=200,
        description="Data points allocated to base detector reference window."
    )
    threshold: float = Field(
        default=0.01,
        description="Warning threshold trigger boundary."
    )
    adaptation_threshold: float = Field(
        default=0.05,
        description="Drift threshold mandatory adapt boundary."
    )
    sampling_interval: int = Field(
        default=10,
        description="Evaluate drift statistics every N streams."
    )

    @field_validator("window_size", "sampling_interval")
    @classmethod
    def validate_positive_ints(cls, val: int) -> int:
        if val <= 0:
            raise ValueError("Window size and sampling interval must be positive.")
        return val

    @field_validator("threshold", "adaptation_threshold")
    @classmethod
    def validate_positive_floats(cls, val: float) -> float:
        if val <= 0.0:
            raise ValueError("Drift warning and adaptation thresholds must be positive.")
        return val


class EvaluationConfig(BaseModel):
    """Configuration describing evaluation rates and locations."""

    metrics: List[str] = Field(
        default_factory=lambda: ["accuracy", "f1_score", "rouge_l", "bleu", "latency_ms"],
        description="Standard metrics recorded during validation."
    )
    plots: List[str] = Field(
        default_factory=lambda: ["loss_curves", "drift_alerts", "confusion_matrix"],
        description="Charts generated and exported during runs."
    )
    output_dir: str = Field(
        default="./experiments/results",
        description="Filsystem location to export test suites output."
    )
    evaluation_frequency: int = Field(
        default=5,
        description="Run validation sweeps every N rounds."
    )

    @field_validator("evaluation_frequency")
    @classmethod
    def validate_freq(cls, val: int) -> int:
        if val <= 0:
            raise ValueError("Evaluation frequency must be a positive integer.")
        return val


class LoggingConfig(BaseModel):
    """Configuration governing logs sinks."""

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="System logging level filter."
    )
    console_logging: bool = Field(
        default=True,
        description="If True, emit outputs to console."
    )
    file_logging: bool = Field(
        default=True,
        description="If True, write records to disk file."
    )
    rotation: str = Field(
        default="10 MB",
        description="File size threshold trigger to rotate file."
    )
    retention: str = Field(
        default="1 month",
        description="Duration window to retain rotated log files."
    )


class ExperimentConfig(BaseModel):
    """Configuration describing active experiment run tags."""

    experiment_name: str = Field(
        default="baseline_personalization",
        description="Identifiable experiment namespace."
    )
    tracker: Literal["wandb", "mlflow", "local"] = Field(
        default="local",
        description="Active experiment tracking client."
    )
    tags: List[str] = Field(
        default_factory=lambda: ["llama3", "fedavg", "adwin"],
        description="Experiment categories tags."
    )
    description: str = Field(
        default="Baseline federated LoRA personalization run.",
        description="Free text summary of experiment purpose."
    )


class AppConfig(BaseModel):
    """Root configuration aggregator for the entire DriftAdapt application."""

    system: SystemConfig = Field(default_factory=SystemConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    lora: LoRAConfig = Field(default_factory=LoRAConfig)
    training: TrainingConfig = Field(default_factory=TrainingConfig)
    federated: FederatedConfig = Field(default_factory=FederatedConfig)
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)
    drift: DriftConfig = Field(default_factory=DriftConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    experiment: ExperimentConfig = Field(default_factory=ExperimentConfig)
