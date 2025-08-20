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

echo "==> Create app directory & venv…"
"${SSH[@]}" bash -s <<EOS
set -euo pipefail
mkdir -p "$APP_DIR"
python3 -m venv "$APP_DIR/.venv"
"$PIP_BIN" install --upgrade pip wheel
EOS

echo "==> Sync project sources to the Pi…"
"${RSYNC[@]}" \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.venv' \
  "${SRC_DIR_LOCAL}/" "${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}:${APP_DIR}/"

echo "==> Install Python dependencies…"
"${SSH[@]}" bash -s <<EOS
set -euo pipefail
"$PIP_BIN" install -r "$APP_DIR/requirements.txt"
EOS

echo "==> Create systemd service…"
"${SSH[@]}" bash -s <<EOS
set -euo pipefail
sudo tee /etc/systemd/system/${SERVICE_NAME} >/dev/null <<UNIT
[Unit]
Description=Gunicorn for Django pihome
After=network.target

[Service]
User=${HOME_PI_USERNAME}
Group=${HOME_PI_USERNAME}
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/.venv/bin
ExecStart=${GUNICORN_BIN} pihome.wsgi:application --bind 127.0.0.1:8000 --workers 2

Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now ${SERVICE_NAME}
sudo systemctl status ${SERVICE_NAME} --no-pager || true
EOS

echo "✅ Init complete. Gunicorn should be listening on 127.0.0.1:8000 on the Pi."
