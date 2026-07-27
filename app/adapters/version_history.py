"""DriftAdapt Adapter Version History.

Author: DriftAdapt Contributors
Purpose: Manages historical lineage and dependency graphs for adapter versions.
"""

from typing import Dict, List, Optional

from app.adapters.version_metadata import AdapterVersionMetadata


class VersionHistoryManager:
    """Provides lookup and traversal methods over version metadata."""
    
    @staticmethod
    def get_history(versions: Dict[str, AdapterVersionMetadata], clinic_id: str) -> List[AdapterVersionMetadata]:
        """Returns all versions for a given clinic, sorted by creation time."""
        clinic_versions = [v for v in versions.values() if v.clinic_id == clinic_id]
        return sorted(clinic_versions, key=lambda v: v.created_at)

    @staticmethod
    def get_latest(versions: Dict[str, AdapterVersionMetadata], clinic_id: str) -> Optional[AdapterVersionMetadata]:
        """Finds the most recent version for a clinic."""
        history = VersionHistoryManager.get_history(versions, clinic_id)
        return history[-1] if history else None

    @staticmethod
    def find_parent(versions: Dict[str, AdapterVersionMetadata], version_id: str) -> Optional[AdapterVersionMetadata]:
        """Finds the parent version of a given version."""
        v = versions.get(version_id)
        if v and v.parent_version:
            return versions.get(v.parent_version)
        return None

    @staticmethod
    def find_children(versions: Dict[str, AdapterVersionMetadata], version_id: str) -> List[AdapterVersionMetadata]:
        """Finds all versions that derive directly from the given version."""
        children = [v for v in versions.values() if v.parent_version == version_id]
        return sorted(children, key=lambda v: v.created_at)

    @staticmethod
    def get_lineage(versions: Dict[str, AdapterVersionMetadata], version_id: str) -> List[AdapterVersionMetadata]:
        """Traces the direct lineage (ancestors) backward from the given version."""
        lineage = []
        current = versions.get(version_id)
        
        while current:
            lineage.append(current)
            if not current.parent_version:
                break
            current = versions.get(current.parent_version)
            
        return lineage
