#!/usr/bin/env bash
# Validate a contract v1 fixture, then send it through Hub's manual-run API. env: PASEO_HUB_URL, PASEO_HUB_API_KEY (scope
# runs:dispatch), PROJECT_SLUG, CONTRACT_DIR (kc-ops-inbox checkout of branch spacedock-ensign/ops-inbox-r1-setup-and-isolation),
# optional FIXTURE (default relay-ceiling-near). Arg 1: deliveryKey. Nothing is sent when validation fails. Never prints the key.
set -euo pipefail
: "${PASEO_HUB_URL:?}" "${PASEO_HUB_API_KEY:?}" "${PROJECT_SLUG:?}" "${CONTRACT_DIR:?}" "${1:?deliveryKey}"
F="$CONTRACT_DIR/contract/fixtures/${FIXTURE:-relay-ceiling-near}.json"
node "$CONTRACT_DIR/contract/validate.mjs" "$F" || { echo "contract v1 refused the event; nothing sent" >&2; exit 1; }
body=$(python3 -I -c 'import json,sys; print(json.dumps({"projectSlug":sys.argv[1],"trigger":"ops-event-poc","actor":"ops-poc-sender","deliveryKey":sys.argv[2],"input":json.load(open(sys.argv[3]))["body"]}))' "$PROJECT_SLUG" "$1" "$F")
curl -sS -o /dev/stdout -w '\nHTTP %{http_code}\n' -X POST "$PASEO_HUB_URL/api/v1/manual-runs" \
  -H "Authorization: Bearer $PASEO_HUB_API_KEY" -H 'Content-Type: application/json' --data "$body"
