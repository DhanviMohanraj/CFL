"""DriftAdapt Request Logging Middleware.

Author: DriftAdapt Contributors
Purpose: Logs HTTP requests, status codes, latencies, and publishes metrics to MetricsBus.
Future Integration: Mounted in app/main.py.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.logging import LoggerFactory
from app.core.metrics import Metric, MetricsBus, MetricType

logger = LoggerFactory.get_logger("RequestLogging")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware logging HTTP requests and recording endpoint execution metrics."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        correlation_id = getattr(request.state, "correlation_id", "N/A")

        response = await call_next(request)

        status_code = response.status_code
        elapsed_ms = getattr(request.state, "elapsed_ms", 0.0)

        # Formatted log entry
        log_msg = f"{method} {path} -> {status_code} ({elapsed_ms:.2f}ms) [client={client_host}, req_id={correlation_id}]"

        if status_code >= 500:
            logger.error(log_msg)
        elif status_code >= 400:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        # Publish request latency metric to MetricsBus
        try:
            bus = MetricsBus()
            metric_name = "http.request_latency_ms"
            if not bus._registry.is_registered(metric_name):
                bus.register_schema(metric_name, MetricType.LATENCY, "HTTP request latency in milliseconds.")

            bus.publish(
                Metric(
                    name=metric_name,
                    value=round(elapsed_ms, 2),
                    module="RequestLoggingMiddleware",
                    metadata={"path": path, "method": method, "status_code": str(status_code)},
                )
            )
        except Exception:
            pass

        return response
