from job_registry import register
from dashboard.models.job import Job
from .logger_job import RunLogger

@register("CALENDAR")
def get_calendar(job: Job, logger: RunLogger, params: dict):
    pass
