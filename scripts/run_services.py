"""
Script to run all microservices simultaneously.

This script starts:
- product-service on port 8001
- user-service on port 8002
- order-service on port 8003
"""

import subprocess
import sys
import time
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_colored(message: str, color: str) -> None:
    """Print message with color."""
    print(f"{color}{message}{Colors.END}")


def main():
    """Main function that runs all services."""

    # Verify we are in the correct directory
    project_root = Path(__file__).parent.parent

    print_colored("\n" + "="*60, Colors.HEADER)
    print_colored("  STARTING MICROSERVICES", Colors.HEADER + Colors.BOLD)
    print_colored("="*60 + "\n", Colors.HEADER)

    # Service configuration
    services = [
        {
            "name": "Product Service",
            "module": "services.product-service.main:app",
            "port": 8001,
            "color": Colors.GREEN
        },
        {
            "name": "User Service",
            "module": "services.user-service.main:app",
            "port": 8002,
            "color": Colors.BLUE
        },
        {
            "name": "Order Service",
            "module": "services.order-service.main:app",
            "port": 8003,
            "color": Colors.YELLOW
        },
    ]

    processes = []

    try:
        # Start each service
        for service in services:
            print_colored(
                f"Starting {service['name']} on port {service['port']}...",
                service['color']
            )

            cmd = [
                sys.executable,  # Use current Python
                "-m",
                "uvicorn",
                service["module"],
                "--host", "0.0.0.0",
                "--port", str(service["port"]),
                "--reload"
            ]

            # Start process
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
                "color": service["color"]
            })

            time.sleep(1)  # Small pause between services

        print_colored("\n" + "="*60, Colors.GREEN)
        print_colored("  ALL SERVICES STARTED", Colors.GREEN + Colors.BOLD)
        print_colored("="*60, Colors.GREEN)

        print("\nAvailable services:")
        print_colored("  Product Service: http://localhost:8001/docs", Colors.GREEN)
        print_colored("  User Service:    http://localhost:8002/docs", Colors.BLUE)
        print_colored("  Order Service:   http://localhost:8003/docs", Colors.YELLOW)

        print_colored("\nPress Ctrl+C to stop all services\n", Colors.HEADER)

        # Keep script running and show logs
        while True:
            for service_info in processes:
                process = service_info["process"]

                # Check if process is still alive
                if process.poll() is not None:
                    print_colored(
                        f"\n[ERROR] {service_info['name']} stopped unexpectedly",
                        Colors.RED
                    )
                    raise KeyboardInterrupt

            time.sleep(1)

    except KeyboardInterrupt:
        print_colored("\n\nStopping services...", Colors.YELLOW)

        # Terminate all processes
        for service_info in processes:
            try:
                service_info["process"].terminate()
                service_info["process"].wait(timeout=5)
                print_colored(
                    f"  {service_info['name']} stopped",
                    service_info["color"]
                )
            except subprocess.TimeoutExpired:
                service_info["process"].kill()
                print_colored(
                    f"  {service_info['name']} forced to close",
                    Colors.RED
                )

        print_colored("\nAll services stopped correctly", Colors.GREEN)
        sys.exit(0)

    except Exception as e:
        print_colored(f"\n[ERROR] {str(e)}", Colors.RED)

        # Clean up processes in case of error
        for service_info in processes:
            try:
                service_info["process"].terminate()
            except:
                pass

        sys.exit(1)


if __name__ == "__main__":
    main()
