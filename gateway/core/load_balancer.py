"""
Load balancer with round-robin strategy.

Distributes requests across multiple service instances.
"""

from typing import List


class LoadBalancer:
    """Round-robin load balancer for service instances."""

    def __init__(self):
        """Initialize load balancer with instance counters."""
        self._counters = {}  # Track current index per service path

    def get_instance(self, path: str, instances: List[str]) -> str:
        """
        Get next instance using round-robin strategy.

        Args:
            path: Service path (used as key for counter)
            instances: List of service URLs

        Returns:
            Selected service URL
        """
        if not instances:
            raise ValueError(f"No instances available for {path}")

        # Single instance, no balancing needed
        if len(instances) == 1:
            return instances[0]

        # Get current counter for this path
        if path not in self._counters:
            self._counters[path] = 0

        # Get instance using round-robin
        index = self._counters[path] % len(instances)
        instance = instances[index]

        # Increment counter for next request
        self._counters[path] = (self._counters[path] + 1) % len(instances)

        return instance
