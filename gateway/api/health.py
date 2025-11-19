from fastapi import APIRouter, Request

from gateway.models.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(status="healthy")


@router.get("/ready", response_model=ReadyResponse)
async def ready(request: Request) -> ReadyResponse:
    """
    Readiness probe for Kubernetes.
    Checks if router and load balancer are initialized.
    """
    router_ready = hasattr(request.app.state, "router") and request.app.state.router is not None
    lb_ready = (
        hasattr(request.app.state, "load_balancer") and request.app.state.load_balancer is not None
    )

    status = "ready" if (router_ready and lb_ready) else "not_ready"

    return ReadyResponse(status=status, router=router_ready, load_balancer=lb_ready)
