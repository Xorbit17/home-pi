# dashboard/management/commands/job_tick.py
from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from croniter import croniter

from dashboard.models.job import Job, Execution
from jobs.logger_job import start_execution_queued
from constants import RUNNING, QUEUED

def _cron_due_this_minute(expr: str, now: datetime) -> bool:
    """True if cron expr fires at 'now' (minute precision)."""
    base = now.replace(second=0, microsecond=0)
    prev = croniter(expr, base + timedelta(minutes=1)).get_prev(datetime)
    return prev == base

def find_eligible_jobs(now: datetime) -> list[Job]:
    candidates = Job.objects.filter(enabled=True)
    return [j for j in candidates if _cron_due_this_minute(j.cron, now)]

def queue_due_jobs(now: datetime):
    due = find_eligible_jobs(now)
    with transaction.atomic():
        for job in due:
            has_active = Execution.objects.filter(
                job=job, status__in=[RUNNING, QUEUED]
            ).exists()
            if not has_active:
                Execution.objects.create(
                    job=job,
                    status=QUEUED,
                    started_at=timezone.now(),
                    params=job.params or {},
                )

def tick_minute() -> None:
    now = timezone.now().replace(second=0, microsecond=0)
    queue_due_jobs(now)

    if Execution.objects.filter(status=RUNNING).exists():
        print("An execution is still running; will try again next minute.")
        return

    for execution in Execution.objects.filter(status=QUEUED).order_by("created_at"):
        start_execution_queued(execution)


class Command(BaseCommand):
    help = "Check which jobs are due this minute and queue/start them."

    def handle(self, *args, **options):
        tick_minute()
        self.stdout.write(self.style.SUCCESS("job_tick completed"))
