#!/usr/bin/env bash
set -euo pipefail
export DJANGO_SETTINGS_MODULE=myproject.settings
python -m uvicorn myproject.asgi:application --host 0.0.0.0 --port 8000
