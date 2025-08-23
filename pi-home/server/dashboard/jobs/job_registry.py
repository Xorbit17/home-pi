from typing import Callable, Dict
from constants import JobKind
from dashboard.jobs.logger_job import RunLogger
from dashboard.models.job import Job, Execution

Handler = Callable[[Job, RunLogger, dict | None], str | None]

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
