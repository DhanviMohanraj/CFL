"""DriftAdapt Adapter Package Builder.

Author: DriftAdapt Contributors
Purpose: Packages adapter weights and metadata for transmission.
"""

import gzip
import hashlib
import json
from typing import Tuple

from app.federated.communication.communication_exceptions import PackageValidationError
from app.federated.communication.communication_schema import AdapterTransmission


class AdapterPackageBuilder:
    """Packages and compresses adapter data for transport."""
    
    def compress(self, payload: bytes) -> bytes:
        """Compresses payload using gzip."""
        return gzip.compress(payload)
        
    def decompress(self, payload: bytes) -> bytes:
        """Decompresses a gzip payload."""
        return gzip.decompress(payload)
        
    def package(self, transmission: AdapterTransmission, weights: bytes) -> bytes:
        """Creates a final binary package including metadata and weights."""
        metadata = transmission.model_dump_json().encode('utf-8')
        
        # Simple framing: [Metadata Length (4 bytes)] + [Metadata] + [Weights]
        meta_len = len(metadata)
        meta_len_bytes = meta_len.to_bytes(4, byteorder='big')
        
        raw_package = meta_len_bytes + metadata + weights
        if transmission.compression:
            return self.compress(raw_package)
        return raw_package
        
    def unpack(self, package: bytes, is_compressed: bool) -> Tuple[AdapterTransmission, bytes]:
        """Unpacks a binary package into metadata and weights."""
        if is_compressed:
            package = self.decompress(package)
            
        if len(package) < 4:
            raise PackageValidationError("Package is too small to contain metadata.")
            
        meta_len = int.from_bytes(package[:4], byteorder='big')
        if len(package) < 4 + meta_len:
            raise PackageValidationError("Package is corrupted or incomplete.")
            
        metadata_bytes = package[4:4+meta_len]
        weights = package[4+meta_len:]
        
        try:
            metadata_dict = json.loads(metadata_bytes.decode('utf-8'))
            transmission = AdapterTransmission(**metadata_dict)
            return transmission, weights
        except Exception as e:
            raise PackageValidationError(f"Failed to unpack metadata: {e}")
            
    def verify(self, transmission: AdapterTransmission, package: bytes) -> bool:
        """Verifies package integrity against transmission metadata."""
        actual_checksum = hashlib.sha256(package).hexdigest()
        if actual_checksum != transmission.checksum:
            raise PackageValidationError("Package checksum mismatch.")
        if len(package) != transmission.package_size:
            raise PackageValidationError("Package size mismatch.")
        return True
