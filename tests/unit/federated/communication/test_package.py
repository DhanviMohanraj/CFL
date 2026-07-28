"""Tests for Adapter Package.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.communication.adapter_package import AdapterPackageBuilder
from app.federated.communication.communication_schema import AdapterTransmission
from app.federated.communication.communication_exceptions import PackageValidationError

def test_package_and_unpack():
    builder = AdapterPackageBuilder()
    
    transmission = AdapterTransmission(
        adapter_id="a1",
        version_id="v1",
        clinic_id="c1",
        session_id="s1",
        communication_round=1,
        package_size=100,
        checksum="hash",
        compression=True
    )
    
    weights = b"fake_weights_data"
    
    package = builder.package(transmission, weights)
    assert len(package) > 0
    
    unpacked_transmission, unpacked_weights = builder.unpack(package, is_compressed=True)
    
    assert unpacked_weights == weights
    assert unpacked_transmission.version_id == "v1"

def test_unpack_corrupted():
    builder = AdapterPackageBuilder()
    with pytest.raises(PackageValidationError):
        builder.unpack(b"123", is_compressed=False)
