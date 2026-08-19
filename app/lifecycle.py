"""DriftAdapt Application Lifespan Module.

Author: DriftAdapt Contributors
Purpose: Manages FastAPI application lifespan context: sequential startup initialization and graceful shutdown cleanup.
Future Integration: Registered as the lifespan parameter of FastAPI() in app/main.py.
"""

import gc
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import torch
from fastapi import FastAPI

from app.container import ServiceContainer
from app.core.logging import LoggerFactory
from app.core.metrics import Metric, MetricType
from app.core.runtime import RuntimeInitializer

logger = LoggerFactory.get_logger("ApplicationLifespan")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI async context manager controlling application startup and shutdown phases."""
    start_time = time.time()
    logger.info("DriftAdapt Application Lifespan STARTUP phase initiated.")

    container = ServiceContainer()

    try:
        # 1. Load ConfigManager
        config_mgr = container.config_manager()
        config = config_mgr.get_config()
        logger.info(f"Loaded ConfigManager configuration for project: {config.system.project_name}")

        # 2. Initialize LoggerFactory
        LoggerFactory.initialize()
        logger.info("LoggerFactory initialization confirmed.")

        # 3. Initialize MetricsBus
        bus = container.metrics_bus()
        logger.info("MetricsBus initialized.")

        # 4-7. Runtime, Environment, Device, Seed, and Directory Verification
        RuntimeInitializer.initialize(config_manager=config_mgr)
        logger.info("Runtime and Device verification completed successfully.")

        # 8-10. Initialize ModelManager, Load Foundation Model, Freeze Parameters
        model_mgr = container.model_manager()
        model_info = model_mgr.load_model()
        logger.info(f"Foundation Model '{model_info.metadata.model_name}' prepared and frozen.")

        # 11-13. Publish Startup Metrics
        startup_duration_ms = (time.time() - start_time) * 1000

        metric_name = "app.startup_time_ms"
        if not bus._registry.is_registered(metric_name):
            bus.register_schema(metric_name, MetricType.SYSTEM, "Total application lifespan startup duration in milliseconds.")

        bus.publish(
            Metric(
                name=metric_name,
                value=round(startup_duration_ms, 2),
                module="ApplicationLifespan",
            )
        )

        # 14. Mark Application Ready
        container.mark_ready(True)
        logger.info(f"DriftAdapt Backend is READY! Total startup duration: {startup_duration_ms:.2f}ms.")

    except Exception as e:
        logger.critical("DriftAdapt Application Lifespan STARTUP failed: {}", str(e), exc_info=True)
        container.mark_ready(False)
        raise e

    yield  # Application serves incoming HTTP requests

    # --- SHUTDOWN PHASE ---
    logger.info("DriftAdapt Application Lifespan SHUTDOWN phase initiated.")
    try:
        # 1. Mark Application Unready
        container.mark_ready(False)

        # 2. Unload Model & Release GPU Memory
        if container._model_manager is not None:
            container.model_manager().unload_model()

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # 3. Flush Metrics
        if container._metrics_bus is not None:
            container.metrics_bus().shutdown()

        logger.info("DriftAdapt Backend shutdown completed gracefully.")
    except Exception as e:
        logger.error(f"Error encountered during application shutdown: {e}")
