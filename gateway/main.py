"""
Smart API Gateway - Main application.

This is the core gateway application that routes requests to backend microservices.
"""

import signal
import sys
import yaml
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from typing import Any, Dict, List

from gateway.api import auth_router, health_router
from gateway.config.settings import settings
from gateway.core.load_balancer import LoadBalancer
from gateway.core.proxy import forward_request
from gateway.core.router import Router
from gateway.middleware.auth import check_auth
from gateway.middleware.logging import LoggingMiddleware
from gateway.middleware.rate_limit import RateLimitMiddleware


# Load routes from YAML configuration
routes_config: List[Dict[str, Any]] = []
router: Router | None = None
load_balancer: LoadBalancer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load configuration on startup and cleanup on shutdown."""
    global routes_config, router, load_balancer

    # Startup
    with open(settings.ROUTES_FILE, "r") as f:
        config = yaml.safe_load(f)
        routes_config = config.get("routes", [])

    # Generate service URLs from replicas configuration
    for route in routes_config:
        if "service" in route:
            service = route["service"]
            port = service.get("port")
            replicas = service.get("replicas", 1)

            # Generate URLs for all replicas
            service_urls = []
            for replica_index in range(replicas):
                instance_port = port + (replica_index * 10)
                service_urls.append(f"http://localhost:{instance_port}")

            # Store generated URLs in route config
            route["service_urls"] = service_urls

    # Initialize router and load balancer
    router = Router(routes_config)
    load_balancer = LoadBalancer()

    # Store in app state for readiness checks
    app.state.router = router
    app.state.load_balancer = load_balancer

    print(f"Loaded {len(routes_config)} routes from configuration")

    yield

    # Shutdown cleanup
    print("Shutting down gateway gracefully...")
    app.state.router = None
    app.state.load_balancer = None


# Initialize FastAPI
app = FastAPI(
    title="Smart API Gateway",
    description="Lightweight API Gateway for microservices with intelligent routing",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middlewares (order matters: last added = first executed)
app.add_middleware(RateLimitMiddleware, default_rpm=100)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)


# Graceful shutdown handler
def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    sys.exit(0)


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


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

    # Get target URL with load balancing
    instances = matched_route["service_urls"]
    target_url = load_balancer.get_instance(matched_route["path"], instances)

    # Log forwarding for verification
    print(f"→ Forwarding {request.method} {full_path} to: {target_url}")

    # Forward request to backend service
    return await forward_request(request, target_url)
