from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Literal
import docker


@dataclass
@dataclass
class ContainerHealth:
    id: str
    name: str
    status: Literal["created","running","restarting","removing","paused","exited","dead"]
    health: Literal["starting","healthy","unhealthy","none"]
    mem_usage: int


def get_container_health() -> List[ContainerHealth]:
    """
    Inspect all containers (running and stopped) and return their status + health info.
    """
    client = docker.from_env()
    containers = []

    for c in client.containers.list(all=True):
        state = c.attrs.get("State", {})
        stats = c.stats(stream=False)
        containers.append(ContainerHealth(
            id=c.id,
            name=c.name,
            status=state.get("Status", "unknown"),
            health=state.get("Health","unknown"),
            mem_usage=stats["memory_stats"]["usage"],
        ))

    return containers


