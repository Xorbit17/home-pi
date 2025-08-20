#!/usr/bin/env bash
set -euo pipefail

openssl req -x509 -nodes -newkey rsa:2048 -days 30 \
  -keyout certs/selfsigned.key -out certs/selfsigned.crt \
  -subj "/CN=$(hostname -f || echo raspberrypi)"