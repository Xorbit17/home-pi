#!/usr/bin/bash
set -euo pipefail

# Load config
ENV_FILE="../.env.aws"
[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE"; exit 1; }
# shellcheck disable=SC1090
source "$ENV_FILE"

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }

export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$AWS_ACCESS_KEY_SECRET
export AWS_REGION=eu-central-1
export AWS_HOSTED_ZONE_ID=$HOSTED_ZONE_ID

lego --accept-tos --email "$EMAIL" \
  --dns route53 \
  --domains "$DOMAIN" \
  --path /etc/lego \
  --dns.resolvers 1.1.1.1 \
  --dns-timeout 300 \
  --dns.disable-cp \
  run

