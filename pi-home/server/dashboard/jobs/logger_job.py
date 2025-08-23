# jobs/logger_job.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, cast
from django.utils import timezone
import traceback
from dashboard.models.job import Job, JobLogEntry, Execution
from constants import RUNNING, QUEUED, SUCCESS, ERROR, JobKind
from job_registry import get_handler
from django.db import transaction

MAX_LINES_PER_RUN = 500

@dataclass
class RunLogger:
    execution: Execution
    _seq: int = 0
    _lines_written: int = 0
    _closed: bool = False
    _agg: Dict[str, int] = field(default_factory=dict)

    def _write(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        if self._closed or self._lines_written >= MAX_LINES_PER_RUN:
            return
        self._seq += 1
        self._lines_written += 1
        # NOTE: either add a JSONField 'context' to JobLogEntry OR drop it here:
        JobLogEntry.objects.create(
            execution=self.execution,
            level=level,
            message=message,
            seq=self._seq,
        )

    def debug(self, msg, **ctx): self._write("DEBUG", msg, ctx or None)
    def info(self, msg, **ctx):  self._write("INFO",  msg, ctx or None)
    def warn(self, msg, **ctx):  self._write("WARN",  msg, ctx or None)
    def error(self, msg, **ctx): self._write("ERROR", msg, ctx or None)

    def incr(self, key: str, by: int = 1):
        self._agg[key] = self._agg.get(key, 0) + by

    def _close_success(self, summary: str = ""):
        if self._closed: return
        self._closed = True
        now = timezone.now()
        started = self.execution.started_at or now
        self.execution.summary = summary[:500]
        self.execution.status = SUCCESS
        self.execution.finished_at = now
        self.execution.runtime_ms = int((now - started).total_seconds() * 1000)
        self.execution.save(update_fields=[
            "summary", "status", "finished_at", "runtime_ms",
            "items_read", "items_written", "items_deleted"
        ])

    def _close_error(self, exc: BaseException, summary: str = ""):
        if self._closed: return
        self._closed = True
        now = timezone.now()
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        self.execution.summary = (summary or str(exc))[:500]
        self.execution.error = tb
        self.execution.status = ERROR
        self.execution.finished_at = now
        started = self.execution.started_at or now
        self.execution.runtime_ms = int((now - started).total_seconds() * 1000)
        self.execution.save(update_fields=[
            "summary", "error", "status", "finished_at", "runtime_ms"
        ])

def start_execution_immediately(job: Job, params: dict | None = None, rethrow: bool = False):
    """TESTING ONLY: run handler now, capture logs; optionally rethrow on error."""
    execution = Execution.objects.create(
        job=job, started_at=timezone.now(), status=RUNNING, params=params or {}
    )
    logger = RunLogger(execution)
    handler = get_handler(cast(JobKind,job.kind))
    try:
        handler(job, logger, execution.params)
        logger._close_success("Job execution succeeded")
    except Exception as e:
        logger._close_error(e, "Job execution failed")
        if rethrow:
            raise
    return logger

@transaction.atomic
def start_execution_queued(execution: Execution):
    # Only flip to RUNNING if it's still QUEUED (prevents double starts)
    updated = (Execution.objects
               .filter(pk=execution.pk, status=QUEUED)
               .update(status=RUNNING, started_at=timezone.now()))
    if not updated:
        return  # someone else started it
    execution.refresh_from_db(fields=["status", "started_at"])

    job = execution.job
    logger = RunLogger(execution)
    handler = get_handler(job.kind)
    try:
        handler(job, logger, execution.params)
        logger._close_success("Job execution succeeded")
    except Exception as e:
        logger._close_error(e, "Job execution failed")
    return logger