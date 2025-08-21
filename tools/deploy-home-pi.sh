#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(pwd)"
ENV_FILE="${REPO_ROOT}/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env not found at ${ENV_FILE}"
  exit 1
fi

# load environment variables
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${HOME_PI_HOST_LOCAL:?missing in .env}"
: "${HOME_PI_USERNAME:?missing in .env}"

LOCAL_DOCKER_DIR="${REPO_ROOT}/pi-home/docker"
DEST_DOCKER_DIR="/home/${HOME_PI_USERNAME}/docker"
LOCAL_AWS_DIR="${REPO_ROOT}/pi-home/aws-manage"
DEST_AWS_DIR="/home/${HOME_PI_USERNAME}/aws-manage"

if [[ ! -d "${LOCAL_DOCKER_DIR}" ]]; then
  echo "ERROR: local docker dir not found: ${LOCAL_DOCKER_DIR}"
  exit 1
fi

SSH_OPTS=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null)
RSYNC="rsync -avz --delete"

# use sshpass if password provided

if command -v sshpass >/dev/null 2>&1; then
  export SSHPASS="${HOME_PI_PASSWORD}"
  RSYNC="sshpass -e rsync -avz --delete -e 'ssh ${SSH_OPTS[*]}'"
  SSH="sshpass -e ssh ${SSH_OPTS[*]} ${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}"
else
  echo "⚠️  HOME_PI_PASSWORD set but sshpass not installed."
  SSH="ssh ${SSH_OPTS[*]} ${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}"
fi


echo "==> Syncing ${LOCAL_DOCKER_DIR} → ${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}:${DEST_DOCKER_DIR}"
eval $RSYNC "${LOCAL_DOCKER_DIR}/" "${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}:${DEST_DOCKER_DIR}/"
eval $RSYNC "${LOCAL_AWS_DIR}/" "${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}:${DEST_AWS_DIR}/"

echo "==> Restarting compose on remote"
$SSH bash -s <<'EOS'
set -e
cd ~/docker
docker compose down || true
docker compose pull || true
docker compose up -d
EOS

echo "✅ Deploy complete"
