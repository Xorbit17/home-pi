#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(pwd)"
ENV_FILE="${REPO_ROOT}/.env"
SSH_OPTS=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null)

echo $ENV_FILE

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env not found at ${ENV_FILE}"
  exit 1
fi

# load environment variables
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

ssh ${SSH_OPTS[*]} ${HOME_PI_USERNAME}@${HOME_PI_HOST_LOCAL}