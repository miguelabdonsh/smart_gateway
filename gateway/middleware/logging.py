import json
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging with correlation IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Start timer
        start_time = time.time()

        # Log request
        self._log_request(request, correlation_id)

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            self._log_error(request, correlation_id, duration, str(e))
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Log response
        self._log_response(request, response, correlation_id, duration)

        return response

    def _log_request(self, request: Request, correlation_id: str) -> None:
        """Log incoming request with structured data."""
        log_data = {
            "event": "request_received",
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.url.query) if request.url.query else None,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        print(json.dumps(log_data))

    def _log_response(
        self, request: Request, response: Response, correlation_id: str, duration: float
    ) -> None:
        """Log outgoing response with structured data."""
        log_data = {
            "event": "request_completed",
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        }
        print(json.dumps(log_data))

    def _log_error(
        self, request: Request, correlation_id: str, duration: float, error: str
    ) -> None:
        """Log error with structured data."""
        log_data = {
            "event": "request_error",
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "duration_ms": round(duration * 1000, 2),
            "error": error,
        }
        print(json.dumps(log_data))
