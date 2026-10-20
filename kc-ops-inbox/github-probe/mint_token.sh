#!/usr/bin/env bash
# Mint a one-hour installation token limited to one repository and the two permissions the probe needs.
# usage: APP_ID=.. INSTALLATION_ID=.. KEY_FILE=/path/app.pem OWNER_REPO=owner/repo mint_token.sh TOKEN_OUT
# Reads KEY_FILE only to sign; prints the granted permissions and expiry, never the token or the key.
set -euo pipefail
OUT=${1:?token output file}
: "${APP_ID:?}" "${INSTALLATION_ID:?}" "${KEY_FILE:?}" "${OWNER_REPO:?}"
API=${API_URL:-https://api.github.com}
b64() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
now=$(date +%s)
head=$(printf '{"alg":"RS256","typ":"JWT"}' | b64)
claims=$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' $((now - 60)) $((now + 540)) "$APP_ID" | b64)
sig=$(printf '%s.%s' "$head" "$claims" | openssl dgst -sha256 -sign "$KEY_FILE" | b64)
jwt="$head.$claims.$sig"
resp=$(mktemp)
trap 'rm -f "$resp"' EXIT
code=$(curl -sS -o "$resp" -w '%{http_code}' -X POST \
  -H "Authorization: Bearer $jwt" -H "Accept: application/vnd.github+json" \
  -d "{\"repositories\":[\"${OWNER_REPO#*/}\"],\"permissions\":{\"contents\":\"write\",\"pull_requests\":\"write\"}}" \
  "$API/app/installations/$INSTALLATION_ID/access_tokens")
[ "$code" = 201 ] || { echo "mint failed: HTTP $code $(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1])).get("message",""))' "$resp")" >&2; exit 1; }
umask 077
python3 -I -c 'import json,sys;open(sys.argv[2],"w").write(json.load(open(sys.argv[1]))["token"])' "$resp" "$OUT"
python3 -I -c 'import json,sys;d=json.load(open(sys.argv[1]));print("permissions",d["permissions"],"repository_selection",d["repository_selection"],"expires_at",d["expires_at"])' "$resp"
