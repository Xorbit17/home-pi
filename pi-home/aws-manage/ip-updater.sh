#!/usr/bin/bash
set -euo pipefail

ensure_time_ok() {
  # Compare local time with an HTTPS server's Date header (no NTP needed)
  local remote local_s skew
  remote="$(curl -fsSI --max-time 5 https://aws.amazon.com | awk -F': ' '/^Date:/{$1=""; sub(/^ /,""); print}')"
  [[ -n "$remote" ]] || return 0   # if offline, skip

  # Convert both to epoch seconds
  local_s="$(date -u +%s)"
  skew="$(( local_s - $(date -u -d "$remote" +%s) ))"
  (( skew<0 )) && skew=$(( -skew ))

  if (( skew > 120 )); then
    echo "[time] Clock skew ${skew}s > 120s, resyncing…" >&2
    sudo timedatectl set-ntp true || true
    sudo systemctl restart systemd-timesyncd || true
    sleep 2
  else
    echo "Time OK"
  fi
}

# Load config
ENV_FILE="../.env.aws"
[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE"; exit 1; }
# shellcheck disable=SC1090
source "$ENV_FILE"

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }

get_ip() {
  local ip
  for url in $IPV4_CHECK_URLS; do
    ip="$(curl -fsS --max-time 3 "$url" | tr -d '[:space:]')" || true
    if [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
      echo "$ip"; return 0
    fi
  done
  return 1
}

main() {
  ensure_time_ok

  local current last
  current="$(get_ip)" || { log "ERROR: could not determine public IPv4"; exit 1; }

  if [[ -f "$STATE_FILE" ]]; then
    last="$(cat "$STATE_FILE" || true)"
  else
    last=""
  fi

  if [[ "$current" == "$last" ]]; then
    log "No change (IPv4=$current)"; exit 0
  fi

  log "IP changed: $last -> $current; updating Route53…"

  CHANGE_BATCH="$(cat <<JSON
{
  "Comment": "Pi DDNS update",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "$RECORD_NAME",
        "Type": "A",
        "TTL": $TTL,
        "ResourceRecords": [{ "Value": "$current" }]
      }
    }
  ]
}
JSON
)"

  aws route53 change-resource-record-sets \
    --profile "$AWS_PROFILE" \
    --hosted-zone-id "$HOSTED_ZONE_ID" \
    --change-batch "$CHANGE_BATCH"
  log "AWS command succeeded"

  echo "$current" | tee "$STATE_FILE"
  chmod 600 "$STATE_FILE"

  log "Route53 UPSERT done (A=$current)"
}

main "$@"
