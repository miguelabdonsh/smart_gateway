"""
Load balancer with round-robin strategy and health checks.

Distributes requests across multiple service instances.
"""

import time
from typing import Dict, List, Set

import httpx


class LoadBalancer:
    """Round-robin load balancer with health checks for service instances."""

    def __init__(self, health_check_interval: int = 30):
        """
        Initialize load balancer with instance counters and health tracking.

        Args:
            health_check_interval: Seconds between health checks
        """
        self._counters: Dict[str, int] = {}  # Track current index per service path
        self._unhealthy_instances: Set[str] = set()  # Track unhealthy instances
        self._last_health_check: Dict[str, float] = {}  # Last check timestamp per instance
        self._health_check_interval = health_check_interval

    def get_instance(self, path: str, instances: List[str]) -> str:
        """
        Get next healthy instance using round-robin strategy.

        Args:
            path: Service path (used as key for counter)
            instances: List of service URLs

        Returns:
            Selected service URL

        Raises:
            ValueError: If no healthy instances available
        """
        if not instances:
            raise ValueError(f"No instances available for {path}")

        # Filter out unhealthy instances
        healthy_instances = [i for i in instances if i not in self._unhealthy_instances]

        if not healthy_instances:
            # All instances unhealthy, try with all instances (give them a chance)
            healthy_instances = instances
            # Clear unhealthy set to retry
            self._unhealthy_instances.clear()

        # Single instance, no balancing needed
        if len(healthy_instances) == 1:
            return healthy_instances[0]

        # Get current counter for this path
        if path not in self._counters:
            self._counters[path] = 0

        # Get instance using round-robin
        index = self._counters[path] % len(healthy_instances)
        instance = healthy_instances[index]

        # Increment counter for next request
        self._counters[path] = (self._counters[path] + 1) % len(healthy_instances)

        return instance

    async def check_health(self, instance_url: str) -> bool:
        """
        Check if an instance is healthy.

        Args:
            instance_url: URL of the instance to check

        Returns:
            True if healthy, False otherwise
        """
        # Check if we need to perform health check (rate limiting)
        now = time.time()
        last_check = self._last_health_check.get(instance_url, 0)

        if now - last_check < self._health_check_interval:
            # Too soon, assume healthy
            return instance_url not in self._unhealthy_instances

        # Perform health check
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{instance_url}/health")
                is_healthy = response.status_code == 200

                # Update tracking
                if is_healthy:
                    self._unhealthy_instances.discard(instance_url)
                else:
                    self._unhealthy_instances.add(instance_url)

                self._last_health_check[instance_url] = now
                return is_healthy
        except Exception:
            # Mark as unhealthy on error
            self._unhealthy_instances.add(instance_url)
            self._last_health_check[instance_url] = now
            return False

    def mark_unhealthy(self, instance_url: str) -> None:
        """Mark an instance as unhealthy (called on request failure)."""
        self._unhealthy_instances.add(instance_url)
