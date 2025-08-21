#!/usr/bin/env bash
set -euo pipefail
# Bootstrap Raspberry Pi
sudo apt-get update -y || true
sudo apt-get upgrade -y || true

# Install Docker (CE) + Compose plugin
sudo apt-get install -y ca-certificates curl gnupg
sudo apt-get install -y awscli
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
sudo systemctl enable --now docker

# (You may need to log out/in once for the docker group to take effect)
docker version && docker compose version

