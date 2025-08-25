from django.db import models
from dashboard.jobs.image_processing_declaration import ART_STYLE_CHOICES
class SourceImage(models.Model):
    path = models.TextField()
    classification = models.JSONField(null=True, default=None)  # null => not classified yet
    has_variants = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"SourceImage({self.pk}): {self.path}"
class Variant(models.Model):
    source_image = models.ForeignKey(
        "SourceImage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rendered_assets",
    )
    path = models.TextField(null=True, default=None) # Null means variant was created but generation has crashed
    art_style = models.CharField(max_length=64, choices=ART_STYLE_CHOICES, null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Variant({self.pk}): {self.path} (artstyle:{self.art_style})"

