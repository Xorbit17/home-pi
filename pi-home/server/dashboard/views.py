from django.shortcuts import render
from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET
from .models.weather import Forecast
from dashboard.jobs.services.select_image import get_variant
import os
import mimetypes
from django.utils import timezone
from datetime import timedelta



def home(request):
    return render(
        request, "dashboard/home.html", {"msg": "Hello from Django templates"}
    )


def dashboard(request):
    now = timezone.now()

    static_fake_data = {
        "header": {
            "hostname": "raspi-pi5",
            "now": now,
            "last_update": now - timedelta(minutes=5),
        },
        "alerts": [
            {"level": "warning", "text": "Disk /data at 85%"},
            {"level": "good", "text": "All containers healthy"},
        ],
        "weather": {
            "updated_at": now,
            "days": [
                {
                    "label": "Today",
                    "tmax": 22,
                    "tmin": 14,
                    "summary": "Cloudy",
                    "wind": "NW 15 km/h",
                    "rain_chance": 30,
                },
                {
                    "label": "Tonight",
                    "tmax": 16,
                    "tmin": 12,
                    "summary": "Clear",
                    "wind": "N 5 km/h",
                    "rain_chance": 5,
                },
                {
                    "label": "Tomorrow",
                    "tmax": 24,
                    "tmin": 15,
                    "summary": "Sunny",
                    "wind": "NE 10 km/h",
                    "rain_chance": 0,
                },
                {
                    "label": "Fri",
                    "tmax": 20,
                    "tmin": 13,
                    "summary": "Rain showers",
                    "wind": "SW 20 km/h",
                    "rain_chance": 70,
                },
                {
                    "label": "Sat",
                    "tmax": 19,
                    "tmin": 12,
                    "summary": "Partly cloudy",
                    "wind": "W 15 km/h",
                    "rain_chance": 20,
                },
            ],
        },
        "system": {
            "updated_at": now,
            "uptime": "12d 04h",
            "load1": 0.25,
            "load5": 0.18,
            "load15": 0.11,
            "cpu_temp": 48,
            "mem_used": 1.2,
            "mem_total": 8,
            "mem_pct": 15,
            "os": "Raspbian GNU/Linux 12 (bookworm)",
        },
        "disks": {
            "updated_at": now,
            "items": [
                {
                    "id": "disk1",
                    "mount": "/",
                    "fs": "ext4",
                    "used": 20.0,
                    "total": 100.0,
                    "pct": 20.0 / 100.0 * 100.0,
                    "pct_unused": (100.0-20.0) / 100.0 * 100.0
                },
                {
                    "id": "disk2",
                    "mount": "/data",
                    "fs": "ext4",
                    "used": 450.0,
                    "total": 1000.0,
                    "pct": 450.0 / 1000.0 * 100.0,
                    "pct_unused": (1000.0-450.0) / 1000.0 * 100.0,
                },
            ],
        },
        "docker": {
            "updated_at": now,
            "containers": [
                {"name": "nginx", "state": "running", "health": "healthy"},
                {"name": "transmission", "state": "exited", "health": "—"},
                {"name": "postgres", "state": "running", "health": "unhealthy"},
            ],
        },
        "calendar": {
            "updated_at": now,
            "today": [
                {
                    "start": now.replace(hour=9, minute=0),
                    "title": "Doctor Ellen",
                    "location": "Clinic",
                },
                {
                    "start": now.replace(hour=14, minute=30),
                    "title": "Project Meeting",
                    "location": "Zoom",
                },
            ],
            "week": [
                {
                    "date": now + timedelta(days=1),
                    "events": [
                        {
                            "start": now.replace(hour=11, minute=0) + timedelta(days=1),
                            "title": "Lunch with Sam",
                            "location": "Café",
                        },
                    ],
                },
                {
                    "date": now + timedelta(days=2),
                    "events": [],
                },
                {
                    "date": now + timedelta(days=3),
                    "events": [
                        {
                            "start": now.replace(hour=18, minute=0) + timedelta(days=3),
                            "title": "Bak’s birthday party",
                            "location": "Firestation",
                        },
                    ],
                },
            ],
        },
    }

    return render(request, "dashboard/dashboard.html", static_fake_data)


def forecast(request):
    forecasts = Forecast.objects.all()[:24]  # cap for now
    return render(request, "dashboard/forecast.html", {"forecasts": forecasts})


def news(request):
    return render(request, "dashboard/news.html")


@require_GET
def photo(request):
    """
    Returns one image (as raw bytes) chosen by final score.
    """
    try:
        chosen = get_variant()
    except Exception:
        raise Http404("Failed to select an image.")

    path = chosen.path
    if not path or not os.path.exists(path):
        raise Http404("Image file not found on disk.")

    ctype, _ = mimetypes.guess_type(path)
    ctype = ctype or "application/octet-stream"

    resp = FileResponse(open(path, "rb"), content_type=ctype)
    # Dynamic content; avoid caching on the client/display unless you want it
    resp["Cache-Control"] = "no-store"
    return resp
