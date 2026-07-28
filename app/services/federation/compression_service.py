"""Compression Service for Federated Updates.

Author: DriftAdapt Contributors
Purpose: Provides compression algorithms (gzip, lzma, zstd) to minimize federated update payload size.
"""

import gzip
import lzma
import time
from typing import Tuple, Dict, Any, Optional

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

from app.core.logging import LoggerFactory


class CompressionService:
    """Service for compressing and decompressing byte payloads."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("CompressionService")

    def compress(self, data: bytes, algorithm: str = "gzip", level: Optional[int] = None) -> Tuple[bytes, Dict[str, Any]]:
        """Compresses byte data using the specified algorithm.
        
        Args:
            data: Raw bytes to compress.
            algorithm: 'gzip', 'lzma', or 'zstd'.
            level: Compression level (algorithm specific). Defaults to a balanced level if None.
            
        Returns:
            Tuple containing:
            - The compressed bytes.
            - A dictionary of statistics (ratio, duration).
            
        Raises:
            ValueError: If the algorithm is unsupported or unavailable.
        """
        start_time = time.perf_counter()
        original_size = len(data)
        
        if algorithm == "gzip":
            lvl = level if level is not None else 6
            compressed_data = gzip.compress(data, compresslevel=lvl)
        elif algorithm == "lzma":
            # lzma is very slow but provides high compression. 
            lvl = level if level is not None else lzma.PRESET_DEFAULT
            compressed_data = lzma.compress(data, preset=lvl)
        elif algorithm == "zstd":
            if not ZSTD_AVAILABLE:
                self._logger.warning("zstandard not installed, falling back to gzip.")
                return self.compress(data, algorithm="gzip", level=level)
            lvl = level if level is not None else 3
            compressor = zstd.ZstdCompressor(level=lvl)
            compressed_data = compressor.compress(data)
        elif algorithm == "none":
            compressed_data = data
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
            
        duration = time.perf_counter() - start_time
        compressed_size = len(compressed_data)
        ratio = compressed_size / original_size if original_size > 0 else 1.0
        
        stats = {
            "algorithm": algorithm,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": ratio,
            "duration_s": duration
        }
        
        self._logger.debug(f"Compression complete: {original_size} -> {compressed_size} bytes ({ratio:.2%} ratio) in {duration:.3f}s.")
        return compressed_data, stats

    def decompress(self, data: bytes, algorithm: str = "gzip") -> bytes:
        """Decompresses byte data.
        
        Args:
            data: Compressed bytes.
            algorithm: 'gzip', 'lzma', 'zstd', or 'none'.
            
        Returns:
            The decompressed raw bytes.
        """
        if algorithm == "gzip":
            return gzip.decompress(data)
        elif algorithm == "lzma":
            return lzma.decompress(data)
        elif algorithm == "zstd":
            if not ZSTD_AVAILABLE:
                raise ValueError("zstandard is not installed but zstd compression was specified.")
            decompressor = zstd.ZstdDecompressor()
            return decompressor.decompress(data)
        elif algorithm == "none":
            return data
        else:
            raise ValueError(f"Unsupported decompression algorithm: {algorithm}")
