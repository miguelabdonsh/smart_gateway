"""
Smart API Gateway - Main application.

This is the core gateway application that routes requests to backend microservices.
"""

import yaml
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from typing import Dict, List, Any

from gateway.config.settings import settings
from gateway.core.proxy import forward_request
from gateway.core.router import Router
from gateway.middleware.auth import check_auth


# Load routes from YAML configuration
routes_config: List[Dict[str, Any]] = []
router: Router | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load configuration on startup and cleanup on shutdown."""
    global routes_config, router

    # Startup
    with open(settings.ROUTES_FILE, "r") as f:
        config = yaml.safe_load(f)
        routes_config = config.get("routes", [])

    # Initialize router
    router = Router(routes_config)

    print(f"Loaded {len(routes_config)} routes from configuration")

    yield

    # Shutdown (cleanup if needed)


# Initialize FastAPI
app = FastAPI(
    title="Smart API Gateway",
    description="Lightweight API Gateway for microservices with intelligent routing",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Gateway health check endpoint.

    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "api-gateway",
        "routes_loaded": len(routes_config)
    }


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_request(request: Request, path: str):
    """
    Route incoming requests to appropriate backend service.

    Args:
        request: Incoming HTTP request
        path: Request path

    Returns:
        Response from backend service
    """
    full_path = f"/{path}"

    # Find matching route using router engine
    matched_route, path_params = router.match(full_path)

    if not matched_route:
        return {"error": "Route not found", "path": full_path}

    # Check authentication
    check_auth(request, routes_config)

    # Forward request to backend service
    target_url = matched_route["service_url"]
    return await forward_request(request, target_url)
