from typing import Callable, Dict
from constants import JobKind
from models.job import Job, Execution
from .logger_job import start_execution, RunLogger

Handler = Callable[[Job, RunLogger, dict], str | None]

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
