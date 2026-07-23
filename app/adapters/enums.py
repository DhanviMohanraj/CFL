"""DriftAdapt Adapter Registry Enums Module.

Author: DriftAdapt Contributors
Purpose: Defines enumerations for the Federated Adapter Registry.
"""

from enum import Enum


class AdapterStatus(str, Enum):
    """Status lifecycle of a federated personalization adapter."""

    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"
