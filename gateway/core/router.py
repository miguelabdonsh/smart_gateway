"""
Router engine with pattern matching.

Handles route matching with exact, prefix, and parameter patterns.
"""

import re
from typing import Dict, List, Any, Tuple


class Router:
    """Route matcher with pattern support."""

    def __init__(self, routes: List[Dict[str, Any]]):
        """
        Initialize router with routes configuration.

        Args:
            routes: List of route configurations from YAML
        """
        self.routes = routes
        self._compile_routes()

    def _compile_routes(self) -> None:
        """Precompile route patterns for faster matching."""
        for route in self.routes:
            path = route["path"]

            # Detect pattern type
            if path.endswith("/*") and (":id" in path or ":user_id" in path):
                # Param + wildcard: /api/users/:id/* -> /api/users/123/anything
                pattern = path[:-2]  # Remove /*
                pattern = pattern.replace(":id", r"([^/]+)").replace(":user_id", r"([^/]+)")
                route["_pattern"] = re.compile(f"^{pattern}/")  # Match prefix
                route["_match_type"] = "param_prefix"
            elif ":id" in path or ":user_id" in path:
                # Parameter pattern: /api/users/:id -> /api/users/123
                pattern = path.replace(":id", r"([^/]+)").replace(":user_id", r"([^/]+)")
                route["_pattern"] = re.compile(f"^{pattern}$")
                route["_match_type"] = "param"
            elif path.endswith("/*"):
                # Prefix pattern: /api/users/* -> /api/users/anything/here
                pattern = path[:-2]  # Remove /*
                route["_pattern"] = pattern
                route["_match_type"] = "prefix"
            else:
                # Exact pattern: /api/users
                route["_pattern"] = path
                route["_match_type"] = "exact"

    def match(self, path: str) -> Tuple[Dict[str, Any] | None, Dict[str, str]]:
        """
        Find matching route for given path.

        Args:
            path: Request path to match

        Returns:
            Tuple of (matched_route, path_params)
            Returns (None, {}) if no match found
        """
        # Priority: exact > param > param_prefix > prefix

        # 1. Try exact matches first
        for route in self.routes:
            if route["_match_type"] == "exact" and route["_pattern"] == path:
                return route, {}

        # 2. Try parameter matches
        for route in self.routes:
            if route["_match_type"] == "param":
                match = route["_pattern"].match(path)
                if match:
                    params = {"id": match.group(1)} if match.groups() else {}
                    return route, params

        # 3. Try param + prefix matches
        for route in self.routes:
            if route["_match_type"] == "param_prefix":
                match = route["_pattern"].match(path)
                if match:
                    params = {"id": match.group(1)} if match.groups() else {}
                    return route, params

        # 4. Try prefix matches
        for route in self.routes:
            if route["_match_type"] == "prefix" and path.startswith(route["_pattern"]):
                return route, {}

        return None, {}
