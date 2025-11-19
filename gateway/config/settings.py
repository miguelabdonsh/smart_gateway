"""
Gateway configuration settings.

Centralized configuration for the API Gateway.
"""

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


settings = Settings()
