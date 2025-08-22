from zoneinfo import ZoneInfo
from typing import Literal, Dict
from pathlib import Path

def parse_env_file(path: str | Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]
            env[key] = value
    return env

LOCAL_TZ = ZoneInfo("Europe/Brussels")
APP_DIR = Path(__file__).resolve().parents[0] # app; a.k.a. the current django app
PROJECT_DIR = APP_DIR.parents[0]   # server; a.k.a the django root
PI_DIR = PROJECT_DIR.parents[0]  # pi_home; a.k.a root of all sources of projects running on this pi
ENV_PATH = PI_DIR / ".env.server"
SECRETS = parse_env_file(ENV_PATH)

IMAGE_DIR = Path(SECRETS["IMAGE_DIR"])
ICAL_GOOGLE_CALENDAR_URL= SECRETS["ICAL_GOOGLE_CALENDAR_URL"]

NEWS_MODE = "news"
PHOTO_MODE = "photo"

MODE_CHOICES = [
    (NEWS_MODE, "Newspaper"),
    (PHOTO_MODE, "Photo"),
]

WEEKDAY_CHOICES = [
    (0, "Mon"),
    (1, "Tue"),
    (2, "Wed"),
    (3, "Thu"),
    (4, "Fri"),
    (5, "Sat"),
    (6, "Sun"),
]

NEWS_KIND = "news"
PHOTO_KIND = "photo"

ASSET_CHOICES = [
    (NEWS_KIND, "Newspaper"),
    (PHOTO_KIND, "Photo")
]

DEBUG = "DEBUG"
INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"

LOG_LEVEL_CHOICES = [
    (DEBUG, "Debug"),
    (INFO, "Info"),
    (WARN, "Warning"),
    (ERROR, "Error"),
]

CALENDAR   = "CALENDAR"
RSS        = "RSS"
WEATHER    = "WEATHER"
PUSH       = "PUSH"
ART        = "ART"
NEWSPAPER  = "NEWSPAPER"

JOB_KIND_CHOICES = [
    (CALENDAR,   "Get calendar"),
    (RSS,        "Get RSS"),
    (WEATHER,    "Get weather"),
    (PUSH,       "Push to displays"),
    (ART,        "Generate art"),
    (NEWSPAPER,  "Generate newspaper"),
]

JobKind = Literal[
    "CALENDAR",
    "RSS",
    "WEATHER",
    "PUSH",
    "ART",
    "NEWSPAPER",
]

RUNNING = "RUNNING"
SUCCESS = "SUCCESS"
SKIPPED = "SKIPPED"
ERROR = "ERROR"
QUEUED = "QUEUED"

JOB_STATUS_CHOICES = [
    (RUNNING, "Running"),
    (SUCCESS, "Success"),
    (SKIPPED, "Skipped"),
    (ERROR, "Error"),
    (QUEUED, "Queued"),
]

JobStatus = Literal[
    "RUNNING",
    "SUCCESS",
    "SKIPPED",
    "ERROR",
    "QUEUED"
]