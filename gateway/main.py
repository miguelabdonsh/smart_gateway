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


# Load routes from YAML configuration
routes_config: List[Dict[str, Any]] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load configuration on startup and cleanup on shutdown."""
    global routes_config

    # Startup
    with open(settings.ROUTES_FILE, "r") as f:
        config = yaml.safe_load(f)
        routes_config = config.get("routes", [])

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

    # Find matching route
    for route in routes_config:
        if full_path.startswith(route["path"]):
            target_url = route["service_url"]
            return await forward_request(request, target_url)

    # No route found
    return {"error": "Route not found", "path": full_path}
