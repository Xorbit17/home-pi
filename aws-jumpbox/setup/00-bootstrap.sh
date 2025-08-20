#!/usr/bin/env bash
set -euo pipefail
# Bootstrap jump box (Ubuntu or AL2023)
sudo apt-get update -y || true
sudo apt-get install -y nginx certbot python3-certbot-nginx
sudo systemctl enable nginx
sudo systemctl start nginx
echo "[jumpbox] Installed nginx + certbot"
