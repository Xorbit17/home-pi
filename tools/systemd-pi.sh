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

# echo "==> Create systemd service…"
# "${SSH[@]}" bash -s <<EOS
# set -euo pipefail
# sudo tee /etc/systemd/system/${SERVICE_NAME} >/dev/null <<UNIT
# [Unit]
# Description=Gunicorn for Django pihome
# After=network.target

# [Service]
# User=${HOME_PI_USERNAME}
# Group=${HOME_PI_USERNAME}
# WorkingDirectory=${APP_DIR}
# Environment=PATH=${APP_DIR}/.venv/bin
# ExecStart=${GUNICORN_BIN} pihome.wsgi:application --bind 0.0.0.0:8000 --workers 2

# Restart=on-failure

# [Install]
# WantedBy=multi-user.target
# UNIT

# sudo systemctl daemon-reload
# sudo systemctl enable --now ${SERVICE_NAME}
# sudo systemctl status ${SERVICE_NAME} --no-pager || true
# EOS

# echo "==> Create systemd service…"
# "${SSH[@]}" bash -s <<EOS
# sudo tee /etc/systemd/system/route53-ddns.service >/dev/null <<'UNIT'
# [Unit]
# Description=Route53 DDNS updater (IPv4)

# [Service]
# Type=oneshot
# EnvironmentFile=/home/pi/.env.aws
# ExecStart=/home/pi/.ip-updater.sh
# UNIT

# # Timer (every 5 min)
# sudo tee /etc/systemd/system/route53-ddns.timer >/dev/null <<'UNIT'
# [Unit]
# Description=Run Route53 DDNS updater every 5 minutes

# [Timer]
# OnBootSec=1min
# OnUnitActiveSec=5min
# AccuracySec=30s
# Persistent=true

# [Install]
# WantedBy=timers.target
# UNIT

# sudo systemctl daemon-reload
# sudo systemctl enable --now route53-ddns.timer
# systemctl list-timers --all | grep route53-ddns || true
# EOS

echo "==> Create systemd service…"
"${SSH[@]}" bash -s <<EOS
sudo tee /etc/systemd/system/route53-ddns.service >/dev/null <<'UNIT'
[Unit]
Description=Fetch weather forecasts

[Service]
Type=oneshot
WorkingDirectory=/home/pi/apps/pihome
Environment="PATH=/home/pi/apps/pihome/.venv/bin:/usr/bin"
ExecStart=/home/pi/apps/pihome/.venv/bin/python manage.py fetch_forecast --location "Blankenberge"

UNIT

# Timer (every 5 min)
sudo tee /etc/systemd/system/forecast.timer >/dev/null <<'UNIT'
[Unit]
Description=Run forecast fetch every 8 hours

[Timer]
OnBootSec=5min
OnUnitActiveSec=8h
Persistent=true

[Install]
WantedBy=timers.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now rforecast.timer
systemctl list-timers --all | grep forecast.timer || true
EOS

