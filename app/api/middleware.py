import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

logger = logging.getLogger(
    "nexusrag.requests"
)


class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):
    """Attach request IDs and log HTTP request completion."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = (
            request.headers.get(
                "X-Request-ID"
            )
            or str(uuid.uuid4())
        )

        start_time = time.perf_counter()

        try:
            response = await call_next(
                request
            )

        except Exception:
            duration_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            logger.exception(
                (
                    "request_failed "
                    "request_id=%s "
                    "method=%s "
                    "path=%s "
                    "duration_ms=%.2f"
                ),
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )

            raise

        duration_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        response.headers[
            "X-Request-ID"
        ] = request_id

        logger.info(
            (
                "request_completed "
                "request_id=%s "
                "method=%s "
                "path=%s "
                "status=%s "
                "duration_ms=%.2f"
            ),
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response