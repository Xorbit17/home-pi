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

lego
# curl -s https://api.github.com/repos/go-acme/lego/releases/latest \
#   | grep "browser_download_url.*linux_arm64.tar.gz" \
#   | cut -d '"' -f 4 \
#   | wget -i -
# tar -xzf lego_v*.tar.gz
# sudo mv lego /usr/local/bin/
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_REGION=eu-central-1
export AWS_HOSTED_ZONE_ID=
lego --email "dennis.vaneecke@gmail.com" \
     --dns route53 \
     --domains "dennisvaneecke.be" \
     --path /etc/lego run \


