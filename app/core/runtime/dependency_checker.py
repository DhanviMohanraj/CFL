"""DriftAdapt Dependency Checker Module.

Author: DriftAdapt Contributors
Purpose: Checks importability and versions of key dependencies, providing diagnostics on missing ones.
Future Integration: Invoked at startup to verify libraries availability.
"""

import importlib.metadata
import importlib.util
from typing import Dict, List, Tuple

# Mapping pip names to import names
DEPENDENCY_MAP: Dict[str, str] = {
    "torch": "torch",
    "transformers": "transformers",
    "peft": "peft",
    "bitsandbytes": "bitsandbytes",
    "accelerate": "accelerate",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "numpy": "numpy",
    "pandas": "pandas",
    "scikit-learn": "sklearn",
    "river": "river",
    "plotly": "plotly",
    "pyyaml": "yaml",
    "pydantic": "pydantic",
    "loguru": "loguru",
    "pytest": "pytest",
}


class DependencyChecker:
    """Verifies library spec presence, imports, and logs diagnostics for missing packages."""

    @classmethod
    def verify_dependencies(cls) -> Tuple[bool, List[str], Dict[str, Dict[str, str]]]:
        """Verifies all mandatory packages.

        Returns:
            Tuple containing:
            - Success boolean (True if all present)
            - List of missing package names
            - Dict of diagnostics details (versions for present, install commands for missing)
        """
        missing: List[str] = []
        diagnostics: Dict[str, Dict[str, str]] = {}

        for pip_name, import_name in DEPENDENCY_MAP.items():
            spec = importlib.util.find_spec(import_name)
            if spec is None:
                # Missing
                missing.append(pip_name)
                diagnostics[pip_name] = {
                    "status": "MISSING",
                    "diagnostics": f"Module '{import_name}' cannot be found. Please install via: pip install {pip_name}",
                }
            else:
                # Present - resolve version
                try:
                    version = importlib.metadata.version(pip_name)
                except importlib.metadata.PackageNotFoundError:
                    # In some custom environments package meta might not be registered
                    try:
                        module = importlib.import_module(import_name)
                        version = getattr(module, "__version__", "unknown")
                    except Exception:
                        version = "unknown"

                diagnostics[pip_name] = {
                    "status": "OK",
                    "version": version,
                }

        success = len(missing) == 0
        return success, missing, diagnostics

    @classmethod
    def get_summary_report(cls) -> str:
        """Generates a text summary of dependencies checks."""
        success, missing, diagnostics = cls.verify_dependencies()
        if success:
            return "All 16 core dependencies are installed and verified."

        lines = ["Dependency verification failed!", f"Missing packages count: {len(missing)}"]
        for pkg in missing:
            lines.append(f"  - {pkg}: {diagnostics[pkg]['diagnostics']}")

        return "\n".join(lines)
