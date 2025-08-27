from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import docker


@dataclass
class ContainerHealth:
    name: str
    status: str             # container state, e.g. "running", "exited"
    health: Optional[str]   # "healthy", "unhealthy", "starting", or None if no healthcheck


def get_container_health() -> List[ContainerHealth]:
    """
    Inspect all containers (running and stopped) and return their status + health info.
    """
    client = docker.from_env()
    containers = []

    for c in client.containers.list(all=True):
        state = c.attrs.get("State", {})
        health = state.get("Health")
        containers.append(ContainerHealth(
            name=c.name,
            status=state.get("Status", "unknown"),
            health=health.get("Status") if health else None,
        ))

    return containers
