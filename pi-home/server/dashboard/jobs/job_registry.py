from typing import Callable, Dict
from dashboard.constants import JobKind, RUNNING, QUEUED
from dashboard.jobs.logger_job import RunLogger
from dashboard.models.job import Job, Execution
from django.utils import timezone

from datetime import datetime
from typing import Optional, Dict, cast
from django.db import transaction

class DummyJob:
    def __init__(
        self,
        kind,
        params = None,
    ):
        self.name = "DummyJob"
        self.kind = kind
        self.cron = None
        self.enabled = True
        self.params = params or {}

        self.last_run_started_at = None
        self.last_run_finished_at = None
        self.last_run_status = None
        self.last_run_message = ""

        self.created_at = timezone.now()
        self.updated_at = timezone.now()

    def __str__(self) -> str:
        return f"DummyJob: {self.name} [{self.kind}]"


Handler = Callable[[Job | DummyJob, RunLogger, dict | None], str | None]

_registry: Dict[str, Handler] = {}

def register(kind: JobKind):
    def deco(fn: Handler):
        _registry[kind] = fn
        return fn
    return deco

def get_handler(kind: JobKind) -> Handler:
    try:
        return _registry[kind]
    except KeyError:
        raise KeyError(f"No handler registered for kind '{kind}'")
    
def test_job(jobKind: JobKind, params: dict | None = None, rethrow: bool = False):
    execution = Execution.objects.create(
        job=None, started_at=timezone.now(), status=RUNNING, params=params or {}
    )
    logger = RunLogger(execution)
    handler = get_handler(jobKind)
    dummy = DummyJob(jobKind)
    try:
        handler(dummy, logger, execution.params)
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
    handler = get_handler(cast(JobKind,job.kind))
    try:
        handler(job, logger, execution.params)
        logger._close_success("Job execution succeeded")
    except Exception as e:
        logger._close_error(e, "Job execution failed")
    return logger
