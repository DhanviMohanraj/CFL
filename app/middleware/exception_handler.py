"""DriftAdapt Global Exception Handler Middleware.

Author: DriftAdapt Contributors
Purpose: Intercepts unhandled exceptions and custom DriftAdapt errors, logging stack trace details and returning structured JSON error payloads.
Future Integration: Mounted in app/main.py.
"""

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger("GlobalExceptionHandler")


class GlobalExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware catching top-level unhandled exceptions during request dispatch."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            correlation_id = getattr(request.state, "correlation_id", "N/A")
            logger.error(
                f"Unhandled Exception during request {request.method} {request.url.path} "
                f"[req_id={correlation_id}]: {exc}",
                exc_info=True,
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "InternalServerError",
                    "message": "An unexpected server error occurred. Please consult system logs.",
                    "details": str(exc),
                    "request_id": correlation_id,
                },
            )
