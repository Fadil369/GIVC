#!/usr/bin/env bash
set -euo pipefail
if docker compose version >/dev/null 2>&1; then DC="docker compose"; else DC="docker-compose"; fi
cd "$(dirname "$0")"
$DC up -d --build
CFG=/etc/cloudflared/config.yml
if [ -f "$CFG" ] && ! grep -q 'workflow.brainsait.com' "$CFG"; then
  sudo cp "$CFG" "$CFG.bak"
  sudo awk '1; /- service: http_status:404/ && !x {print "  - hostname: workflow.brainsait.com\n    service: http://localhost:3001\n  - hostname: api.brainsait.com\n    service: http://localhost:8000\n  - hostname: n8n.brainsait.com\n    service: http://localhost:5678\n  - hostname: ai.brainsait.com\n    service: http://localhost:3000"; x=1; next}' "$CFG" | sudo tee "$CFG.new" >/dev/null && sudo mv "$CFG.new" "$CFG"
  sudo systemctl restart cloudflared || true
fi
printf "\nServices:\n"; docker ps --format '{{.Names}} -> {{.Ports}} | {{.Status}}' | grep -E 'brainsait-|portainer|wordpress|moodle' || true
printf "\nLocal ports status:\n"; for p in 3001 8000 5678 3000 8080 8081 9000; do printf "$p: "; curl -sI http://localhost:$p | head -n1 || true; done
