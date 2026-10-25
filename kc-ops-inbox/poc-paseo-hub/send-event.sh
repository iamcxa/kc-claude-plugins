#!/usr/bin/env bash
# Send the fixture ops event through Hub's manual-run API. env: PASEO_HUB_URL, PASEO_HUB_API_KEY (scope runs:dispatch),
# PROJECT_SLUG. Arg 1: deliveryKey. Prints the HTTP status and the response body, never the key.
set -euo pipefail
: "${PASEO_HUB_URL:?}" "${PASEO_HUB_API_KEY:?}" "${PROJECT_SLUG:?}" "${1:?deliveryKey}"
HERE=$(cd "$(dirname "$0")" && pwd)
body=$(python3 -I -c 'import json,sys; print(json.dumps({"projectSlug":sys.argv[1],"trigger":"ops-event-poc","actor":"ops-poc-sender","deliveryKey":sys.argv[2],"input":open(sys.argv[3]).read().strip()}))' "$PROJECT_SLUG" "$1" "$HERE/fixture-event.json")
curl -sS -o /dev/stdout -w '\nHTTP %{http_code}\n' -X POST "$PASEO_HUB_URL/api/v1/manual-runs" \
  -H "Authorization: Bearer $PASEO_HUB_API_KEY" -H 'Content-Type: application/json' --data "$body"
