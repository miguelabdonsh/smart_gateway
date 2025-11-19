"""
JWT token utilities for authentication.

Validates JWT tokens from external authentication services.
"""

import jwt
from typing import Dict, Any

from gateway.config.settings import settings


def verify_token(token: str) -> Dict[str, Any] | None:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None
