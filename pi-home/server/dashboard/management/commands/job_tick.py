# dashboard/management/commands/job_tick.py
from datetime import timedelta, datetime
from dashboard.constants import RUNNING, QUEUED, CRON

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from croniter import croniter

from dashboard.models.job import Job, Execution
from dashboard.jobs.job_registry import start_execution_queued
# Load job modules to make sure they are registered
import dashboard.jobs.dummy_job
import dashboard.jobs.generate_variant
import dashboard.jobs.classify

ACTIVE_STATUSES = [RUNNING, QUEUED]

def _cron_due_this_minute(expr: str, now: datetime) -> bool:
    """True if cron expr fires at 'now' (minute precision)."""
    base = now.replace(second=0, microsecond=0)
    prev = croniter(expr, base + timedelta(minutes=1)).get_prev(datetime)
    return prev == base


def find_eligible_jobs(now: datetime) -> list[Job]:
    base_minute = now.replace(second=0, microsecond=0)

    active_execs = Execution.objects.filter(
        job=OuterRef("pk"),
        status__in=ACTIVE_STATUSES,
    )

    qs = (
        Job.objects
        .filter(cron__isnull=False, enabled=True, job_type=CRON)
        # Exclude jobs that already finished within this same minute
        .filter(Q(last_run_finished_at__isnull=True) | Q(last_run_finished_at__lt=base_minute))
        .annotate(active_exists=Exists(active_execs))
    )

    # Keep only those whose cron fires this minute and have no active execution
    return [
        j for j in qs
        if _cron_due_this_minute(j.cron or "", now) and not j.active_exists # type: ignore
    ]

def queue_due_jobs(now: datetime):
    base_minute = now.replace(second=0, microsecond=0)
    due = find_eligible_jobs(now)

    with transaction.atomic():
        for job in due:
            # Re-check to avoid races between selection and insert
            already_running = Execution.objects.filter(
                job=job, status__in=ACTIVE_STATUSES
            ).exists()
            finished_this_minute = (
                job.last_run_finished_at is not None
                and job.last_run_finished_at >= base_minute
            )

            if not already_running and not finished_this_minute:
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
