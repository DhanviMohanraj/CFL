"""Packaging Statistics Schema for Federated Updates.

Author: DriftAdapt Contributors
Purpose: Schema for tracking the performance and resource utilization of the packaging process.
"""

from pydantic import BaseModel, Field


class PackagingStatistics(BaseModel):
    """Statistics covering compression, encryption, and overall packaging."""
    
    original_size: int = Field(..., description="Size of the raw serialized payload in bytes")
    compressed_size: int = Field(..., description="Size after compression in bytes")
    compression_ratio: float = Field(..., description="Ratio of compressed_size to original_size")
    packaging_time: float = Field(..., description="Total time taken to package (serialize + compress + encrypt) in seconds")
    encryption_time: float = Field(..., description="Time taken strictly for encryption in seconds")
    upload_time: float = Field(..., description="Time taken to upload (if tracking post-transmission)")
