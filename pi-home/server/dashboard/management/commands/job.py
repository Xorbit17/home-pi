import dashboard.jobs.classify
from django.core.management.base import BaseCommand
from dashboard.constants import JOB_KIND_CHOICES, JobKind, RUNNING
from dashboard.models.job import Execution, Job
from django.utils import timezone
from dashboard.jobs.job_registry import test_job
from typing import cast



VALID_CHOICES =  [t[0] for t in JOB_KIND_CHOICES]

class Command(BaseCommand):
    help = "Prints a greeting"

    def add_arguments(self, parser):
        # positional argument
        parser.add_argument("job_kind", type=str)

    def handle(self, *args, **options):
        job_kind = options["job_kind"]
        try:
            VALID_CHOICES.index(job_kind)
        except ValueError:
            print(f"Job kind {job_kind} does not exist. Allowed values are {','.join(VALID_CHOICES)}")
        test_job(cast(JobKind, job_kind))

