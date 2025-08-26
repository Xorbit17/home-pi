# dashboard/management/commands/seed.py
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from dashboard.models.job import Job 
from dashboard.constants import CRON, CLASSIFY, ART, DUMMY


class Command(BaseCommand):
    help = "Seed initial data: periodic jobs, etc."

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Creates or updates a minimal set of cron-based jobs.
        Runs safely multiple times (idempotent).
        """
        seed_jobs = [
            {
                "name": "classify-new-images",
                "kind": CLASSIFY,   
                "job_type": CRON,
                "cron": "*/5 * * * *",  # every 5 minutes
                "enabled": True,
                "params": {},           # add API keys or tuning knobs later if needed
            },
            {
                "name": "generate-art-variants",
                "kind": ART,
                "job_type": CRON,
                "cron": "0 0 * * *",    # every day at midnight
                "enabled": True,
                "params": {},
            },
            {
                "name": "dummy-heartbeat",
                "kind": DUMMY,
                "job_type": CRON,
                "cron": "* * * * *",    # every minute
                "enabled": True,
                "params": {},
            },
        ]

        created, updated = 0, 0

        for spec in seed_jobs:
            obj, was_created = Job.objects.update_or_create(
                name=spec["name"],
                defaults={
                    "kind": spec["kind"],
                    "job_type": spec["job_type"],
                    "cron": spec["cron"],
                    "enabled": spec["enabled"],
                    "params": spec["params"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created job: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated job: {obj.name}"))

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. Created: {created}, Updated: {updated}"))
