#!/usr/bin/env bash
set -euo pipefail
# Bootstrap Raspberry Pi
sudo apt-get update -y || true
sudo apt-get install -y nginx certbot python3-certbot-dns-route53
sudo systemctl enable nginx
sudo systemctl start nginx
echo "[pi] Installed nginx + certbot (dns-route53 plugin)"
