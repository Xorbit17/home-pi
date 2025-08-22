# app/services/assets.py
from django.utils import timezone
from app.models.assets import RenderedAsset, NEWS_KIND, PHOTO_KIND

def latest_asset(kind: str, display=None) -> RenderedAsset | None:
    now = timezone.now()
    qs = RenderedAsset.objects.filter(kind=kind, valid_from__lte=now)
    if display:
        qs = qs.filter(display__in=[display, None])  # prefer per-display, then global
    if qs.exists():
        # pick the first whose valid_until is null or in the future
        for a in qs:
            if not a.valid_until or a.valid_until > now:
                return a
    return None
