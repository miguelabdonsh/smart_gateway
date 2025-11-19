"""
Authentication middleware.

Validates JWT tokens on protected routes.
"""

from fastapi import Request, HTTPException, status
from typing import Dict, List, Any

from gateway.utils.jwt_utils import verify_token


def check_auth(request: Request, routes_config: List[Dict[str, Any]]) -> None:
    """
    Check if request requires authentication and validate token.

    Args:
        request: Incoming HTTP request
        routes_config: List of route configurations

    Raises:
        HTTPException: If auth required and token invalid
    """
    path = request.url.path

    # Find matching route
    route_config = None
    for route in routes_config:
        if path.startswith(route["path"]):
            route_config = route
            break

    # Check if route requires auth
    if not route_config or not route_config.get("auth_required", False):
        return

    # Extract token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = auth_header.split(" ")[1]

    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Attach user info to request state
    request.state.user = payload.get("sub")
