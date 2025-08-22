# app/models/assets.py
from django.db import models
from django.utils import timezone
from constants import ASSET_CHOICES

class RanderedAsset(models.Model):
    sourceImage = models.ForeignKey("SourceImage")
    # Optional: tie an asset to a specific display; leave null for global
    # validity window (optional, handy for daily newspapers)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["kind", "display", "valid_from"]),
        ]
        ordering = ["-valid_from", "-created_at"]

class SourceImage(models.Model):
    path = models.TextField()
    classification = models.TextField(max_length=20, null=True, default=None) # NO, BAD, PASSABLE, GOOD, VERY_GOOD (None is not yet classified)
    classification_reason = models.TextField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
