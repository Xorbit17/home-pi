from django.db import models, transaction
from django.utils import timezone
from django.core.validators import MinValueValidator

from __future__ import annotations
from datetime import datetime, timedelta
from croniter import croniter
from typing import Optional
from config import DEFAULT_LOCK_SECS
from constants import LOG_LEVELS;

class Job(models.Model):
    """
    A periodic job. Schedules are cron-like ("*/5 * * * *").
    Each job has a 'kind' that picks a Python handler from a registry.
    """
    name = models.CharField(max_length=120, unique=True)
    kind = models.CharField(max_length=64)   # e.g. "news.ingest", "calendar.sync"
    cron = models.CharField(max_length=64, help_text="Cron format, e.g. '0 5 * * *'")
    enabled = models.BooleanField(default=True)

    # Optional parameters for the handler
    params = models.JSONField(default=dict, blank=True)

    # Health / observability
    last_run_started_at = models.DateTimeField(null=True, blank=True)
    last_run_finished_at = models.DateTimeField(null=True, blank=True)
    last_run_status = models.CharField(max_length=20, null=True, blank=True)  # "success" | "error" | "skipped"
    last_run_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["enabled", "next_run_at"]),
            models.Index(fields=["kind"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.kind})"

class Execution(models.Model):
    """
    One row per execution attempt (claimed run).
    """
    job = models.ForeignKey("Job", on_delete=models.CASCADE, related_name="executions")
    started_at = models.DateTimeField(null=True, default=None)
    finished_at = models.DateTimeField(null=True, default=None)

    status = models.CharField(max_length=20, null=True, blank=True)  # running|success|error|skipped
    summary = models.CharField(max_length=500, blank=True, default="")  # short message for dashboards
    error = models.TextField(blank=True, default="")                   # full traceback if any

    created_at = models.DateTimeField(auto_now_add=True)

    params = models.JSONField(null=True, default=None)

    class Meta:
        indexes = [
            models.Index(fields=["job", "-started_at"]),
            models.Index(fields=["status"]),
        ]


class JobLogEntry(models.Model):
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE, related_name="logs")
    ts = models.DateTimeField(default=timezone.now, db_index=True)
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default="INFO", db_index=True)
    message = models.TextField()
    # A monotonic counter to preserve order without depending on timestamps
    seq = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["execution", "seq"]),
            models.Index(fields=["level", "ts"]),
        ]
        ordering = ["seq"]

