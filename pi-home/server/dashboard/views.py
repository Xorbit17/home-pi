from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from .models.weather import Forecast
from dashboard.jobs.services.scoring import calculate_final_score
from dashboard.models.photos import Variant
from typing import Iterable, List, Tuple
import os
import random
import mimetypes
from bisect import bisect

def _weighted_choice(items: Iterable[Tuple[Variant, float]]) -> Variant:
    """
    Select a Variant using weighted random by score.
    Expects (variant, weight) pairs with weight >= 0.
    """
    variants: List[Variant] = []
    cumulative: List[float] = []
    total = 0.0

    for v, w in items:
        if w <= 0.0:
            continue
        total += w
        variants.append(v)
        cumulative.append(total)

    if total == 0.0 or not variants:
        raise Http404("No displayable images with positive score.")

    r = random.random() * total
    idx = bisect(cumulative, r)
    return variants[idx]


def home(request):
    return render(request, "dashboard/home.html", {"msg": "Hello from Django templates"})

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
    # 1) Pull candidates. You can add extra filters if needed.
    qs = Variant.objects.only(
        "id", "path", "score", "favourite", "created_at"
    ).filter(path__isnull=False)

    if not qs.exists():
        raise Http404("No images available.")

    # 2) Build (variant, final_score)
    now = timezone.now()
    pairs: List[Tuple[Variant, float]] = []
    for v in qs.iterator():
        # v.score is your persisted static score
        final_score = calculate_final_score(
            static_score=float(v.score or 0.0),
            favourite=bool(v.favourite),
            created_at=v.created_at,
        )
        pairs.append((v, final_score))

    # 3) Pick one by weighted random
    try:
        chosen = _weighted_choice(pairs)
    except Http404:
        raise
    except Exception:
        raise Http404("Failed to select an image.")

    # 4) Stream file
    path = chosen.path
    if not path or not os.path.exists(path):
        raise Http404("Image file not found on disk.")

    ctype, _ = mimetypes.guess_type(path)
    ctype = ctype or "application/octet-stream"

    resp = FileResponse(open(path, "rb"), content_type=ctype)
    # Dynamic content; avoid caching on the client/display unless you want it
    resp["Cache-Control"] = "no-store"
    return resp
