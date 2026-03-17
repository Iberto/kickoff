import uuid
from time import perf_counter

import structlog
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Add request ID and timing to all requests"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = perf_counter()

        # Bind request context to logger
        # clear to avoid leak between different requests
        structlog.contextvars.clear_contextvars()
        # and then a clear new context
        structlog.contextvars.bind_contextvars(
            request_id=request_id, method=request.method, path=request.url.path
        )

        logger.info("request_started")
        response = await call_next(request)

        duration_ms = (perf_counter() - start_time) * 1000
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Request-Time-Ms"] = str(round(duration_ms, 2))

        return response
        return response
