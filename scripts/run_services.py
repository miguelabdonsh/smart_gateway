"""
Script to run all backend microservices.

This script starts:
- product-service on port 8001
- user-service on port 8002
- order-service on port 8003

Usage:
    uv run scripts/run_services.py
"""

import subprocess
import sys
import time
from pathlib import Path


def main():
    """Main function that runs all backend microservices."""

    project_root = Path(__file__).parent.parent

    print("\n" + "="*60)
    print("  STARTING BACKEND MICROSERVICES")
    print("="*60 + "\n")

    services = [
        {
            "name": "Product Service",
            "module": "services.product-service.main:app",
            "port": 8001,
        },
        {
            "name": "User Service",
            "module": "services.user-service.main:app",
            "port": 8002,
        },
        {
            "name": "Order Service",
            "module": "services.order-service.main:app",
            "port": 8003,
        },
    ]

    processes = []

    try:
        for service in services:
            print(f"Starting {service['name']} on port {service['port']}...")

            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                service["module"],
                "--host", "0.0.0.0",
                "--port", str(service["port"]),
                "--reload"
            ]

            process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            processes.append({
                "process": process,
                "name": service["name"],
                "port": service["port"],
            })

            time.sleep(1)

        print("\n" + "="*60)
        print("  ALL MICROSERVICES STARTED")
        print("="*60)

        print("\nAvailable services:")
        print("  Product Service: http://localhost:8001/docs")
        print("  User Service:    http://localhost:8002/docs")
        print("  Order Service:   http://localhost:8003/docs")

        print("\nPress Ctrl+C to stop all services\n")

        while True:
            for service_info in processes:
                if service_info["process"].poll() is not None:
                    print(f"\n[ERROR] {service_info['name']} stopped unexpectedly")
                    raise KeyboardInterrupt
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping services...")

        for service_info in processes:
            try:
                service_info["process"].terminate()
                service_info["process"].wait(timeout=5)
                print(f"  {service_info['name']} stopped")
            except subprocess.TimeoutExpired:
                service_info["process"].kill()
                print(f"  {service_info['name']} forced to close")

        print("\nAll services stopped correctly")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

        for service_info in processes:
            try:
                service_info["process"].terminate()
            except:
                pass

        sys.exit(1)


if __name__ == "__main__":
    main()
