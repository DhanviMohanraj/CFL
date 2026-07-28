"""DriftAdapt Adapter Metrics Schema.

Author: DriftAdapt Contributors
Purpose: Defines Pydantic models for various metric collections.
"""

import time

from pydantic import BaseModel, Field


class AdapterMetrics(BaseModel):
    """Core metrics associated with an adapter version."""
    adapter_id: str = Field(..., description="Base adapter ID.")
    clinic_id: str = Field(..., description="Clinic ID.")
    version_id: str = Field(..., description="Version ID.")
    communication_round: int = Field(..., description="Federated round.")
    parameter_count: int = Field(..., description="Number of parameters.")
    adapter_size_bytes: int = Field(..., description="Raw byte size.")
    serialized_size_bytes: int = Field(..., description="Serialized size on disk.")
    compressed_size_bytes: int = Field(..., description="Compressed size.")
    checksum: str = Field(..., description="Payload checksum.")
    storage_path: str = Field(..., description="Path where stored.")
    creation_timestamp: float = Field(default_factory=time.time, description="POSIX timestamp.")


class CommunicationMetrics(BaseModel):
    """Metrics related to transmission cost estimations."""
    estimated_upload_bytes: int = Field(..., description="Estimated bytes uploaded.")
    estimated_download_bytes: int = Field(..., description="Estimated bytes downloaded.")
    total_transfer_bytes: int = Field(..., description="Total bytes transferred.")
    compression_ratio: float = Field(..., description="Ratio of compressed to uncompressed.")
    serialization_time_ms: float = Field(..., description="Time taken to serialize.")
    deserialization_time_ms: float = Field(..., description="Time taken to deserialize.")
    estimated_network_time_ms: float = Field(..., description="Calculated network latency.")
    bandwidth_used: str = Field(..., description="Profile of bandwidth used (e.g. 'wifi').")
    communication_efficiency: float = Field(..., description="Efficiency metric.")


class PerformanceMetrics(BaseModel):
    """Metrics for computational overhead."""
    merge_time_ms: float = Field(..., description="Time to merge.")
    load_time_ms: float = Field(..., description="Time to load.")
    save_time_ms: float = Field(..., description="Time to save.")
    validation_time_ms: float = Field(..., description="Time to validate.")
    checksum_time_ms: float = Field(..., description="Time to compute checksum.")
    memory_usage_mb: float = Field(..., description="Current memory consumption.")
    cpu_time_ms: float = Field(..., description="CPU time spent.")
    peak_memory_mb: float = Field(..., description="Peak memory overhead.")
