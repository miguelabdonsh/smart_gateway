import time
from typing import Callable

from cachetools import TTLCache
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory rate limiting middleware using TTLCache.
    Implements sliding window per client IP or JWT subject.
    """

    def __init__(self, app, default_rpm: int = 100):
        super().__init__(app)
        self.default_rpm = default_rpm
        # Cache: key = (client_id, route_path), value = list of request timestamps
        # TTL = 60 seconds (sliding window)
        self.cache: TTLCache = TTLCache(maxsize=10000, ttl=60)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier (IP or JWT subject)
        client_id = self._get_client_id(request)

        # Get route configuration if available
        route_config = getattr(request.state, "route_config", None)

        # Determine rate limit
        if route_config and route_config.rate_limit:
            rpm = route_config.rate_limit.requests_per_minute
        else:
            rpm = self.default_rpm

        # Create cache key
        cache_key = (client_id, request.url.path)

        # Get or create request timestamps list
        now = time.time()
        if cache_key not in self.cache:
            self.cache[cache_key] = []

        timestamps = self.cache[cache_key]

        # Remove timestamps older than 60 seconds (sliding window)
        timestamps[:] = [ts for ts in timestamps if now - ts < 60]

        # Check rate limit
        if len(timestamps) >= rpm:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "limit": rpm,
                    "window": "60 seconds",
                },
                headers={
                    "X-RateLimit-Limit": str(rpm),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60",
                },
            )

        # Add current timestamp
        timestamps.append(now)
        self.cache[cache_key] = timestamps

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, rpm - len(timestamps))
        response.headers["X-RateLimit-Limit"] = str(rpm)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from JWT subject or IP address.
        Priority: JWT sub > Client IP
        """
        # Try to get from JWT
        user = getattr(request.state, "user", None)
        if user:
            return f"user:{user}"

        # Fallback to client IP
        if request.client:
            return f"ip:{request.client.host}"

        return "unknown"
