# app/models/assets.py
from django.db import models
from django.utils import timezone
from constants import ASSET_CHOICES

class RenderedAsset(models.Model):
    kind = models.CharField(max_length=16, choices=ASSET_CHOICES)
    # Optional: tie an asset to a specific display; leave null for global
    display = models.ForeignKey("schedule.Display", null=True, blank=True, on_delete=models.CASCADE)

    image = models.FileField(upload_to="renders/")   # store PNGs
    # validity window (optional, handy for daily newspapers)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["kind", "display", "valid_from"]),
        ]
        ordering = ["-valid_from", "-created_at"]
