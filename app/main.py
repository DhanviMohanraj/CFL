"""DriftAdapt FastAPI Main Application Module.

Author: DriftAdapt Contributors
Purpose: Entry point instantiating FastAPI app, mounting middlewares, registering routers, and configuring lifespan.
Future Integration: Executed by Uvicorn server (uvicorn app.main:app --host 0.0.0.0 --port 8000).
"""

from fastapi import FastAPI

from app.lifecycle import lifespan
from app.middleware.correlation_id import CorrelationIDMiddleware
from app.middleware.exception_handler import GlobalExceptionHandlerMiddleware
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.timing import RequestTimingMiddleware
from app.routes.health import router as health_router
from app.routes.model import router as model_router
from app.routes.ready import router as ready_router
from app.routes.system import router as system_router
from app.routes.training import router as training_router
from app.routes.federation import router as federation_router
from app.routes.aggregation import router as aggregation_router


def create_app() -> FastAPI:
    """Creates and configures the production-grade DriftAdapt FastAPI application."""
    application = FastAPI(
        title="DriftAdapt AI Research Platform API",
        description=(
            "Continual Federated LoRA Personalization of Foundation Models "
            "for Privacy-Preserving Health Advisory Systems in Low-Resource Settings."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Mount Middlewares (Execution order: top-to-bottom for outer layers)
    application.add_middleware(GlobalExceptionHandlerMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(RequestTimingMiddleware)
    application.add_middleware(CorrelationIDMiddleware)

    # Register Routers
    application.include_router(health_router)
    application.include_router(ready_router)
    application.include_router(system_router)
    application.include_router(model_router)
    application.include_router(training_router)
    application.include_router(federation_router)
    application.include_router(aggregation_router)

    return application


# Global FastAPI application instance for Uvicorn ASGI server
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
