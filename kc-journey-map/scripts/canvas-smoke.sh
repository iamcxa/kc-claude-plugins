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

export JOURNEY_API_PORT="${JOURNEY_API_PORT:-0}"
ROOM="smoke-$$"
ROOMS_DIR="$(mktemp -d)"
EXAMPLE="skills/kc-journey-map/references/journey.example.yaml"

cleanup() {
  [ -n "${SERVER_PID:-}" ] && kill "$SERVER_PID" 2>/dev/null || true
  rm -rf "$ROOMS_DIR"
}
trap cleanup EXIT

# Use this process's startup log; a shared-port health check can hit another canvas.
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

# Every projection selected, so the smoke exercises the schema validator against all of
# them, not only the default one board.
PAGES="story-map,journey-board,function-map"
node lib/journey-render.mjs "$EXAMPLE" "$ROOM" --pages "$PAGES"

node - "$ROOM" "$PORT" "$EXAMPLE" "$PAGES" <<'NODE'
const [room, port, example, selection] = process.argv.slice(2)
const { loadJourney, buildAllPages } = await import('./lib/render.mjs')

const model = loadJourney(example)
const built = buildAllPages(model, null, selection.split(','))
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

DRIFT=$(node lib/journey-read.mjs "$EXAMPLE" "$ROOM" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const d=JSON.parse(s);const n=Object.values(d).filter(v=>Array.isArray(v)?v.length:v).length;console.log(n)})')
[ "$DRIFT" = "0" ] || { echo "FAIL: a freshly rendered room reports drift"; exit 1; }

echo "ok  round trip clean"
