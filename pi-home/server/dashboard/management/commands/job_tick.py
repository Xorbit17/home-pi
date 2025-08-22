# minute_tick.py
from django.utils import timezone
from datetime import timedelta, datetime
from croniter import croniter

from models.job import Job, Execution
from jobs.logger_job import start_execution_queued, queue_execution
from constants import RUNNING, QUEUED

def _cron_due_this_minute(expr: str, now: datetime) -> bool:
    """True if cron expr fires at 'now' (minute precision)."""
    base = now.replace(second=0, microsecond=0)
    prev = croniter(expr, base + timedelta(minutes=1)).get_prev(datetime)
    return prev == base

def find_eligible_jobs(now: datetime) -> list[Job]:
    candidates = Job.objects.filter(enabled=True)
    return [j for j in candidates if _cron_due_this_minute(j.cron, now)]

def tick_minute() -> None:
    now = timezone.now().replace(second=0, microsecond=0)
    for job in find_eligible_jobs(now):
        has_active = Execution.objects.filter(
            job=job, status__in=[RUNNING, QUEUED]
        ).exists()
        if not has_active:
            queue_execution(job, params=(job.params or {}))

    # 2) If anything is running, do nothing else this minute
    if Execution.objects.filter(status=RUNNING).exists():
        print("An execution is still running; will try again next minute.")
        return

    # 3) Start queued runs (FIFO). If you truly want one-at-a-time, start only the first().
    for execution in Execution.objects.filter(status=QUEUED).order_by("created_at"):
        start_execution_queued(execution)

tick_minute()
