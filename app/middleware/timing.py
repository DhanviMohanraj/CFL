"""DriftAdapt Request Timing Middleware.

Author: DriftAdapt Contributors
Purpose: Measures HTTP request execution latency in milliseconds and attaches X-Response-Time-MS header.
Future Integration: Mounted in app/main.py.
"""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware measuring request execution time and attaching X-Response-Time-MS header."""

    HEADER_NAME = "X-Response-Time-MS"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        request.state.elapsed_ms = elapsed_ms

        response.headers[self.HEADER_NAME] = f"{elapsed_ms:.2f}"
        return response
