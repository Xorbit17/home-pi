#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(pwd)"
ENV_FILE="${REPO_ROOT}/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env not found at ${ENV_FILE}"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${HOME_PI_HOST_LOCAL:?missing in .env}"
: "${HOME_PI_USERNAME:?missing in .env}"

APP_DIR="/home/${HOME_PI_USERNAME}/apps/pihome"
SRC_DIR_LOCAL="${REPO_ROOT}/pi-home/server"
PY_BIN="/home/${HOME_PI_USERNAME}/apps/pihome/.venv/bin/python"
PIP_BIN="/home/${HOME_PI_USERNAME}/apps/pihome/.venv/bin/pip"
GUNICORN_BIN="/home/${HOME_PI_USERNAME}/apps/pihome/.venv/bin/gunicorn"
SERVICE_NAME="gunicorn-pihome.service"

SSH_OPTS=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null)

# choose ssh/rsync with optional sshpass
RSYNC=(rsync -avz --delete)
SSH=(ssh "${SSH_OPTS[@]}" "${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}")
if [[ -n "${HOME_PI_PASSWORD:-}" ]] && command -v sshpass >/dev/null 2>&1; then
  export SSHPASS="${HOME_PI_PASSWORD}"
  RSYNC=(sshpass -e rsync -avz --delete -e "ssh ${SSH_OPTS[*]}")
  SSH=(sshpass -e ssh "${SSH_OPTS[@]}" "${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}")
fi

# 0) sanity
if [[ ! -d "$SRC_DIR_LOCAL" ]]; then
  echo "ERROR: local source dir not found: $SRC_DIR_LOCAL"
  exit 1
fi

echo "==> Stop service (if running)…"
"${SSH[@]}" sudo systemctl stop "${SERVICE_NAME}" || true

echo "==> Sync project sources to the Pi…"
"${RSYNC[@]}" \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.venv' \
  "${SRC_DIR_LOCAL}/" "${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}:${APP_DIR}/"

echo "==> Start service…"
"${SSH[@]}" sudo systemctl start "${SERVICE_NAME}"
"${SSH[@]}" systemctl status "${SERVICE_NAME}" --no-pager || true

echo "✅ Deploy complete."
