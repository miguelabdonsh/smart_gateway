"""
HTTP proxy functionality for forwarding requests to backend services.

This module handles the actual HTTP forwarding from the gateway to microservices.
"""

import httpx
from typing import Dict, Any
from fastapi import Request, Response
from gateway.config.settings import settings


async def forward_request(
    request: Request,
    target_url: str
) -> Response:
    """
    Forward HTTP request to target service.

    Args:
        request: Incoming FastAPI request
        target_url: Target service base URL

    Returns:
        Response from the backend service
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
