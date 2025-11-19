from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"


class ReadyResponse(BaseModel):
    """Readiness check response."""

    status: str = "ready"
    router: bool
    load_balancer: bool
