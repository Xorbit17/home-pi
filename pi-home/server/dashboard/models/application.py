from django.db import models
from django.utils import timezone
from constants import ART_STYLE_CHOICES
class SourceImage(models.Model):
    path = models.TextField()
    classification = models.JSONField(null=True, default=None)  # null => not classified yet

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"SourceImage({self.id}): {self.path}"
class RenderedAsset(models.Model):
    source_image = models.ForeignKey(
        "SourceImage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rendered_assets",
    )
    path = models.TextField()
    art_style = models.CharField(max_length=64, choices=ART_STYLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        src = f"src={self.source_image_id}" if self.source_image_id else "src=None"
        return f"RenderedAsset({self.id}): {self.art_style} ({src})"
