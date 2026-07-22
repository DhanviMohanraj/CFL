"""DriftAdapt Correlation ID Middleware.

Author: DriftAdapt Contributors
Purpose: Generates or propagates request trace UUIDs (X-Request-ID) across HTTP requests and responses.
Future Integration: Mounted in app/main.py.
"""

import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware attaching unique correlation UUIDs to incoming requests and outgoing responses."""

    HEADER_NAME = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract existing request ID header or generate new UUID
        correlation_id = request.headers.get(self.HEADER_NAME) or str(uuid.uuid4())

        # Store on request state for access in endpoints or downstream middleware
        request.state.correlation_id = correlation_id

        response = await call_next(request)

        # Attach to outgoing response header
        response.headers[self.HEADER_NAME] = correlation_id
        return response
