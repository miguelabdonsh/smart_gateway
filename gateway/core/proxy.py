"""
HTTP proxy functionality for forwarding requests to backend services.

This module handles the actual HTTP forwarding from the gateway to microservices.
"""

import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from gateway.config.settings import settings


async def forward_request(
    request: Request, target_url: str, max_retries: int = 1
) -> Response:
    """
    Forward HTTP request to target service with retry logic.

    Args:
        request: Incoming FastAPI request
        target_url: Target service base URL
        max_retries: Maximum number of retry attempts (default: 1)

    Returns:
        Response from the backend service

    Raises:
        HTTPException: If all retry attempts fail
    """
    # Build full target URL with path and query params
    path = request.url.path
    query = str(request.url.query)
    full_url = f"{target_url}{path}"
    if query:
        full_url = f"{full_url}?{query}"

    # Prepare headers (exclude host header)
    headers = dict(request.headers)
    headers.pop("host", None)

    # Get request body if present
    body = await request.body()

    # Retry loop
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            # Forward request to backend service
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.request(
                    method=request.method,
                    url=full_url,
                    headers=headers,
                    content=body,
                )

            # Return response to client
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
            last_error = e
            # Only retry on network/timeout errors
            if attempt < max_retries:
                continue
            # All retries exhausted
            break

        except Exception as e:
            # Don't retry on other exceptions
            last_error = e
            break

    # All attempts failed
    return JSONResponse(
        status_code=503,
        content={
            "error": "Service unavailable",
            "detail": f"Failed to reach backend service: {str(last_error)}",
            "target": target_url,
        },
    )
