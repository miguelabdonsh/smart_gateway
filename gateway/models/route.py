from typing import Optional

from pydantic import BaseModel, Field


class RateLimitConfig(BaseModel):
    """Rate limiting configuration for a route."""

    requests_per_minute: int = Field(..., gt=0)


class RouteConfig(BaseModel):
    """Route configuration model matching routes.yaml structure."""

    path: str
    service_name: str
    service_namespace: str = "default"
    service_port: int = Field(..., gt=0, lt=65536)
    auth_required: bool = False
    rate_limit: Optional[RateLimitConfig] = None
    timeout_seconds: int = Field(default=5, gt=0)
