"""DriftAdapt Runtime Initializer Module.

Author: DriftAdapt Contributors
Purpose: Resolves configurations, validates dependencies, initializes seeds/devices, and publishes initialization metrics.
Future Integration: Invoked at platform boot by main scripts.
"""

import time
from typing import Dict, Any, List

from app.core.config import ConfigManager
from app.core.logging import LoggerFactory
from app.core.runtime.dependency_checker import DependencyChecker
from app.core.runtime.environment import EnvironmentManager
from app.core.runtime.exceptions import DependencyMissingError, RuntimeInitializationError
from app.core.runtime.runtime_info import RuntimeInfo

logger = LoggerFactory.get_logger("RuntimeInitializer")


class RuntimeInitializer:
    """Orchestrates system verification, device resolution, seed assignment, and metrics logging on boot."""

    @classmethod
    def initialize(cls) -> RuntimeInfo:
        """Runs the entire system startup pipeline.

        Returns:
            RuntimeInfo: The compiled startup report object.

        Raises:
            DependencyMissingError: If a required library is missing.
            RuntimeInitializationError: For other fatal initialization failures.
        """
        # Defer imports to break circular dependencies
        from app.core.device import DeviceManager
        from app.core.seed import SeedManager
        from app.core.metrics import MetricsBus, Metric

        start_time = time.time()
        logger.info("DriftAdapt startup sequence initiated.")

        try:
            # 1. Load configuration
            config_mgr = ConfigManager()
            config = config_mgr.get_config()
            logger.info("System configuration loaded successfully.")

            # 2. Verify environment directories
            env_snap = EnvironmentManager.get_environment_snapshot()
            dir_verif = env_snap["directory_verification"]
            missing_dirs = [name for name, exists in dir_verif.items() if not exists]
            if missing_dirs:
                logger.warning(
                    f"Required project directories are missing from workspace: {missing_dirs}. "
                    "Please execute 'python scripts/bootstrap.py' to generate folders."
                )

            # 3. Verify core dependencies
            all_ok, missing_deps, dep_diagnostics = DependencyChecker.verify_dependencies()
            if not all_ok:
                summary = DependencyChecker.get_summary_report()
                logger.error(f"Dependency check failed:\n{summary}")
                raise DependencyMissingError(
                    f"Startup blocked due to missing core Python dependencies: {missing_deps}. "
                    "Run 'pip install -r requirements/dev.txt' or install them manually."
                )
            logger.info("All core software dependencies verified.")

            # 4. Initialize device and hardware
            dev_mgr = DeviceManager()
            # Pass preferred device from system configs
            device = dev_mgr.resolve_device(config.system.device)
            logger.info(f"Target execution hardware resolved to: {device}")

            # 5. Initialize seeds
            # Pass seed and deterministic settings from configs
            SeedManager.set_seed(
                seed=config.system.random_seed,
                deterministic=config.system.deterministic,
            )

            # 6. Generate consolidated RuntimeInfo
            hardware_summary = dev_mgr.get_hardware_summary()
            dep_report = {
                "all_verified": all_ok,
                "missing": missing_deps,
                "diagnostics": dep_diagnostics,
            }
            exec_report = {
                "device": str(device),
                "random_seed": config.system.random_seed,
                "deterministic": config.system.deterministic,
            }

            runtime_report = RuntimeInfo(
                project_name=config.system.project_name,
                project_version=config.system.project_version,
                timestamp=time.time(),
                environment=env_snap,
                hardware=hardware_summary,
                dependencies=dep_report,
                execution=exec_report,
            )

            # Print formatted report to console log
            logger.info(f"System startup complete.\n{runtime_report.get_summary_report()}")

            # 7. Publish initialization metrics to MetricsBus
            init_duration_ms = (time.time() - start_time) * 1000
            bus = MetricsBus()

            # Wait, let's verify if metrics schemas are registered before publishing,
            # or register them if they are not already registered!
            if not bus._registry.is_registered("runtime.initialization_time_ms"):
                from app.core.metrics.metric_types import MetricType

                bus.register_schema(
                    "runtime.initialization_time_ms",
                    MetricType.RESOURCE,
                    "Runtime boot sequence duration in milliseconds.",
                )

            bus.publish(
                Metric(
                    name="runtime.initialization_time_ms",
                    value=round(init_duration_ms, 2),
                    module="RuntimeInitializer",
                )
            )

            return runtime_report

        except DependencyMissingError:
            raise
        except Exception as e:
            logger.critical(f"DriftAdapt startup failed with unexpected error: {e}")
            raise RuntimeInitializationError(f"Fatal error during system startup initialization: {e}") from e
