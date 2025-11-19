"""
Script to run the API Gateway.

This script starts the gateway on port 8000.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Main function that runs the API Gateway."""

    project_root = Path(__file__).parent.parent

    print("\n" + "="*60)
    print("  STARTING API GATEWAY")
    print("="*60 + "\n")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "gateway.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]

    try:
        print("Starting API Gateway on port 8000...")
        subprocess.run(cmd, cwd=project_root)

    except KeyboardInterrupt:
        print("\n\nGateway stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
