from django.db import models
from dashboard.jobs.image_processing_declaration import (
    ART_STYLE_CHOICES, 
    QUALITY_CLASSIFICATION_CHOICES,
    CONTENT_TYPE_CLASSIFICATION_CHOICES,
    
)


class MinuteSystemSample(models.Model):
    # wall-clock minute start (e.g., 2025-08-26 17:32:00+02:00)
    minute = models.DateTimeField(unique=True, db_index=True)

    # CPU
    cpu_percent_avg = models.FloatField()

    # Memory (bytes)
    mem_total = models.BigIntegerField()
    mem_used_avg = models.BigIntegerField()
    mem_available_avg = models.BigIntegerField()

    # Swap (bytes)
    swap_total = models.BigIntegerField(null=True)
    swap_used_avg = models.BigIntegerField(null=True)

    # Network rates averaged over the minute (bytes/sec)
    rx_bps_avg = models.FloatField(null=True)
    tx_bps_avg = models.FloatField(null=True)

    class Meta:
        ordering = ["-minute"]
    
