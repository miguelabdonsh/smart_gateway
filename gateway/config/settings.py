"""
Gateway configuration settings.

Centralized configuration for the API Gateway.
"""

import os
from pathlib import Path


class Settings:
    """Gateway configuration settings."""

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Paths
    CONFIG_DIR: Path = Path(__file__).parent
    ROUTES_FILE: Path = CONFIG_DIR / "routes.yaml"

    # HTTP client settings
    REQUEST_TIMEOUT: int = 30  # seconds

    # JWT settings (for validating tokens from external auth services)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
