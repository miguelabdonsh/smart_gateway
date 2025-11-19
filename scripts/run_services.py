"""
Script to run all backend microservices with configurable replicas.

Reads gateway/config/routes.yaml (single source of truth).

Usage:
    uv run scripts/run_services.py
"""

import subprocess
import sys
import time
import yaml
from pathlib import Path


def main():
    """Main function that runs all backend microservices."""

    project_root = Path(__file__).parent.parent
    config_file = project_root / "gateway" / "config" / "routes.yaml"

    # Load routes configuration
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    routes = config.get("routes", [])

    # Extract unique services (avoid duplicates from multiple routes)
    services_map = {}
    for route in routes:
        service = route.get("service", {})
        service_name = service.get("name")
        if service_name and service_name not in services_map:
            services_map[service_name] = service

    services = list(services_map.values())

    print("\n" + "="*60)
    print("  STARTING BACKEND MICROSERVICES")
    print("="*60 + "\n")

    processes = []

    try:
        for service in services:
            replicas = service.get("replicas", 1)
            base_port = service.get("port")
            module = service.get("module")

            # Start replicas
            for replica_index in range(replicas):
                port = base_port + (replica_index * 10)
                instance_name = service["name"]
                if replicas > 1:
                    instance_name += f" #{replica_index + 1}"

                print(f"Starting {instance_name} on port {port}...")

                cmd = [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    module,
                    "--host", "0.0.0.0",
                    "--port", str(port),
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
                    "name": instance_name,
                    "port": port,
                })

                time.sleep(1)

        print("\n" + "="*60)
        print("  ALL MICROSERVICES STARTED")
        print("="*60)

        print("\nRunning instances:")
        for proc in processes:
            print(f"  {proc['name']}: http://localhost:{proc['port']}/docs")

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
