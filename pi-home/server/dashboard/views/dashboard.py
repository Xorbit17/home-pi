from dataclasses import dataclass, asdict
from dashboard.models.weather import Forecast
from typing import List, Tuple, Dict, Literal
from datetime import datetime, timedelta
from dashboard.services.machine_stats import MachineStats
from dashboard.services.docker_health import ContainerHealth
from django.shortcuts import render
from django.views import View
from django.utils import timezone


@dataclass
class DashboardAlert:
    level: Literal["info", "warning", "error"]
    message: str


@dataclass
class DashboardHeader:
    hostname: str
    generated_at: datetime
    alerts: List[DashboardAlert]


@dataclass
class WeatherDay:
    label: str
    tmax: float
    tmin: float
    summary: str
    wind_bft: float
    rain_chance_percent: int
    icon: str


@dataclass
class DashboardWeather:
    days: List[WeatherDay]
    updated_at: datetime


@dataclass
class DashboardMetric:
    start_time: datetime
    end_time: datetime
    machinestats: MachineStats
    updated_at: datetime


@dataclass
class DiskStat:
    id: str
    disk_name: str
    disk_used_percent: float
    disk_unused_percent: float
    used: int
    total: int


@dataclass
class DashboardDisks:
    updated_at: datetime
    disks: List[DiskStat]


@dataclass
class GraphStat:
    id: str
    color: str
    labels: List[int]
    values: List[float]


@dataclass
class DashboardStat:
    updated_at: datetime
    stat_id_and_grid: str
    stat_icon_path: str
    stat_title: str
    graph_data: List[GraphStat]


@dataclass
class DashboardDockerHealth:
    updated_at: datetime
    total_memory_used: int
    containers: List[ContainerHealth]


@dataclass
class DashboardStats:
    memory: DashboardStat
    cpu: DashboardStat
    network: DashboardStat


@dataclass
class DashboardData:
    header: DashboardHeader
    weather: DashboardWeather
    disks: DashboardDisks
    stats: DashboardStats
    docker: DashboardDockerHealth


now = timezone.now()

dashboard_data = DashboardData(
    header=DashboardHeader(
        hostname="raspi-01",
        generated_at=now,
        alerts=[
            DashboardAlert(level="info", message="System booted cleanly."),
            DashboardAlert(level="warning", message="Disk usage above 80%."),
        ],
    ),
    weather=DashboardWeather(
        updated_at=now,
        days=[
            WeatherDay(
                label="Monday",
                tmax=23.5,
                tmin=15.2,
                summary="Sunny with light clouds",
                wind_bft=3,
                rain_chance_percent=10,
                icon="clear-day.svg",
            ),
            WeatherDay(
                label="Tuesday",
                tmax=19.1,
                tmin=12.0,
                summary="Light rain showers",
                wind_bft=4,
                rain_chance_percent=60,
                icon="rain.svg",
            ),
            WeatherDay(
                label="Wednesday",
                tmax=19.1,
                tmin=12.0,
                summary="Light rain showers",
                wind_bft=4,
                rain_chance_percent=60,
                icon="rainbow.svg",
            ),
            WeatherDay(
                label="Thursday",
                tmax=19.1,
                tmin=12.0,
                summary="Light rain showers",
                wind_bft=4,
                rain_chance_percent=60,
                icon="hail.svg",
            ),
        ],
    ),
    disks=DashboardDisks(
        updated_at=now,
        disks=[
            DiskStat(
                id="sda",
                disk_name="/dev/sda1",
                disk_used_percent=78.2,
                disk_unused_percent=21.8,
                used=10,
                total=100,
            ),
            DiskStat(
                id="sdb",
                disk_name="/dev/sdb1",
                disk_used_percent=45.0,
                disk_unused_percent=55.0,
                used=10,
                total=100,
            ),
        ],
    ),
    stats=DashboardStats(
        memory=DashboardStat(
            updated_at=now,
            stat_id_and_grid="memory",
            stat_icon_path="svg/tabler/device-sd-card.svg",
            stat_title="Memory Usage",
            graph_data=[
                GraphStat(
                    id="mem",
                    color="blue",
                    labels=list(range(10)),
                    values=[40 + i * 0.5 for i in range(10)],  # fake %
                )
            ],
        ),
        cpu=DashboardStat(
            updated_at=now,
            stat_id_and_grid="cpu",
            stat_icon_path="svg/tabler/cpu.svg",
            stat_title="CPU Usage",
            graph_data=[
                GraphStat(
                    id="cpu",
                    color="green",
                    labels=list(range(10)),
                    values=[10 + i * 2 for i in range(10)],  # fake %
                )
            ],
        ),
        network=DashboardStat(
            updated_at=now,
            stat_id_and_grid="network",
            stat_icon_path="svg/tabler/arrows-left-right.svg",
            stat_title="Network Traffic",
            graph_data=[
                GraphStat(
                    id="net-up",
                    color="orange",
                    labels=list(range(10)),
                    values=[i * 5 for i in range(10)],  # fake kbps
                ),
                GraphStat(
                    id="net-down",
                    color="purple",
                    labels=list(range(10)),
                    values=[50 - i * 3 for i in range(10)],  # fake kbps
                ),
            ],
        ),
    ),
    docker=DashboardDockerHealth(
        updated_at=now,
        total_memory_used=512 * 1024 * 1024,  # 512 MB
        containers=[
            ContainerHealth(
                id="abc123",
                name="nginx",
                status="running",
                health="healthy",
                mem_usage=10,
            ),
            ContainerHealth(
                id="def456",
                name="redis",
                status="running",
                health="unhealthy",
                mem_usage=10,
            ),
            ContainerHealth(
                id="ghi789", name="worker", status="exited", health="none", mem_usage=10
            ),
        ],
    ),
)


class DashboardView(View):
    def get(self, request):
        now = timezone.now()
        # Get alerts; for now empty list
        header = DashboardHeader(
            hostname="Raspberrypi",
            generated_at=now,
            alerts=[]
        )
        weather=DashboardWeather(
            updated_at=now,
            days=[
                WeatherDay(
                    label="Monday",
                    tmax=23.5,
                    tmin=15.2,
                    summary="Sunny with light clouds",
                    wind_bft=3,
                    rain_chance_percent=10,
                    icon="clear-day.svg",
                ),
                WeatherDay(
                    label="Tuesday",
                    tmax=19.1,
                    tmin=12.0,
                    summary="Light rain showers",
                    wind_bft=4,
                    rain_chance_percent=60,
                    icon="rain.svg",
                ),
            ],
        ),
        return render(request, "dashboard/dashboard.html", context=asdict(dashboard_data))
