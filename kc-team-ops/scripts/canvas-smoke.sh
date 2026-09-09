#!/usr/bin/env bash
# Boots the canvas server, renders the worked example into a throwaway room, and asserts
# the document came back with the shapes the model produces.
#
# This is the check that answers "can somebody who installed this actually run it". The
# unit tests prove the model builds records; only booting the server and pushing them
# through the schema validator proves the records are accepted. No browser is involved —
# the client is not exercised here.
set -euo pipefail

cd "$(dirname "$0")/.."

# The server picks its own port and reports it. Choosing one here first raced with the
# probe socket's own close, and on a developer's machine 5858 is usually taken anyway.
export JOURNEY_API_PORT="${JOURNEY_API_PORT:-0}"
ROOM="smoke-$$"
ROOMS_DIR="$(mktemp -d)"
EXAMPLE="skills/kc-journey-map/references/journey.example.yaml"

cleanup() {
  [ -n "${SERVER_PID:-}" ] && kill "$SERVER_PID" 2>/dev/null || true
  rm -rf "$ROOMS_DIR"
}
trap cleanup EXIT

# Waiting for /health alone is not enough: if the bind fails, some other canvas already
# listening on that port answers happily and the whole check passes without this server
# ever having started. The server's own startup line is the identity assertion.
LOG="$ROOMS_DIR/server.log"
JOURNEY_ROOMS_DIR="$ROOMS_DIR" npx tsx ./server/canvas-server.ts >"$LOG" 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 60); do
  grep -q "doc API on http://127.0.0.1:" "$LOG" 2>/dev/null && break
  sleep 0.5
done
PORT=$(sed -n 's|.*doc API on http://127.0.0.1:\([0-9][0-9]*\).*|\1|p' "$LOG" | head -1)
if [ -z "$PORT" ]; then
  echo "FAIL: this server never started"
  sed -n '1,20p' "$LOG"
  exit 1
fi
export JOURNEY_API_PORT="$PORT"
curl -sf "http://127.0.0.1:$PORT/health" >/dev/null || { echo "FAIL: server started but does not answer"; exit 1; }

node lib/journey-render.mjs "$EXAMPLE" "$ROOM"

# The renderer reports what it sent; this reads back what the server kept, so a record
# the validator silently dropped would show up as a count mismatch rather than a pass.
node - "$ROOM" "$PORT" "$EXAMPLE" <<'NODE'
const [room, port, example] = process.argv.slice(2)
// Expected shapes and pages both come from the model, so adding a page is not a change
// this check has to be told about. Hard-coding the page list broke it the first time a
// third page arrived.
const { loadJourney, buildAllPages } = await import('./lib/render.mjs')

const model = loadJourney(example)
const built = buildAllPages(model)
const expected = new Set(built.filter((r) => r.typeName === 'shape').map((r) => r.id))
const expectedPages = built.filter((r) => r.typeName === 'page').map((r) => r.name).sort()

const doc = await fetch(`http://127.0.0.1:${port}/doc?room=${room}`).then((r) => r.json())
const got = new Set(doc.snapshot.documents.map((d) => d.state).filter((r) => r.typeName === 'shape').map((r) => r.id))

const missing = [...expected].filter((id) => !got.has(id))
if (missing.length) {
  console.error(`FAIL: ${missing.length} shape(s) never landed, e.g. ${missing.slice(0, 3).join(', ')}`)
  process.exit(1)
}
const pages = doc.snapshot.documents.map((d) => d.state).filter((r) => r.typeName === 'page').map((r) => r.name).sort()
if (pages.join() !== expectedPages.join()) {
  console.error(`FAIL: expected ${JSON.stringify(expectedPages)}, got ${JSON.stringify(pages)}`)
  process.exit(1)
}
if (pages.length < 2) {
  console.error(`FAIL: the example must exercise more than one page, got ${JSON.stringify(pages)}`)
  process.exit(1)
}
console.log(`ok  ${expected.size} shapes across ${pages.length} pages: ${pages.join(', ')}`)
NODE

# Reading the freshly rendered room back must report no drift, or the two halves disagree.
DRIFT=$(node lib/journey-read.mjs "$EXAMPLE" "$ROOM" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const d=JSON.parse(s);const n=Object.values(d).filter(v=>Array.isArray(v)?v.length:v).length;console.log(n)})')
[ "$DRIFT" = "0" ] || { echo "FAIL: a freshly rendered room reports drift"; exit 1; }

echo "ok  round trip clean"
