"""Bandwidth Optimizer Service for Federated Transmission.

Author: DriftAdapt Contributors
Purpose: Selects optimal transmission configurations based on estimated bandwidth and payload size.
"""

from typing import Dict, Any

from app.core.logging import LoggerFactory


class BandwidthOptimizer:
    """Recommends transmission settings to optimize for speed vs CPU cost."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("BandwidthOptimizer")

    def optimize(
        self,
        payload_size_bytes: int,
        estimated_bandwidth_mbps: float,
        battery_level: float = 1.0
    ) -> Dict[str, Any]:
        """Calculates optimal compression strategies.
        
        Args:
            payload_size_bytes: The estimated uncompressed byte size.
            estimated_bandwidth_mbps: Bandwidth in Megabits per second.
            battery_level: Battery percentage (0.0 to 1.0) to constrain heavy CPU algorithms.
            
        Returns:
            Dictionary containing recommended settings and estimations.
        """
        # Convert MBps to bytes per second for calculations
        bandwidth_bps = (estimated_bandwidth_mbps * 1024 * 1024) / 8
        
        # Default fallback
        recommended_algo = "gzip"
        
        if estimated_bandwidth_mbps > 50.0:
            # High bandwidth, compression is less critical, favor speed
            recommended_algo = "none" if payload_size_bytes < 5_000_000 else "zstd"
        elif estimated_bandwidth_mbps < 5.0:
            # Low bandwidth, heavily compress
            if battery_level > 0.3:
                recommended_algo = "lzma"
            else:
                recommended_algo = "gzip"  # save battery
        else:
            # Medium bandwidth
            recommended_algo = "zstd"
            
        # Very rough estimations for a typical LoRA update
        if recommended_algo == "lzma":
            estimated_compressed_size = payload_size_bytes * 0.15
        elif recommended_algo == "zstd":
            estimated_compressed_size = payload_size_bytes * 0.25
        elif recommended_algo == "gzip":
            estimated_compressed_size = payload_size_bytes * 0.30
        else:
            estimated_compressed_size = float(payload_size_bytes)
            
        estimated_upload_time_s = estimated_compressed_size / bandwidth_bps if bandwidth_bps > 0 else float('inf')
        
        recommendations = {
            "recommended_compression": recommended_algo,
            "estimated_compressed_size": int(estimated_compressed_size),
            "estimated_upload_time_s": estimated_upload_time_s
        }
        
        self._logger.debug(
            f"Bandwidth optimization complete. Recommended '{recommended_algo}' "
            f"for {payload_size_bytes/(1024*1024):.2f}MB payload over {estimated_bandwidth_mbps}Mbps link."
        )
        
        return recommendations
