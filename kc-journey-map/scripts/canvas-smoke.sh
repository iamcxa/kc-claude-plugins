#!/usr/bin/env bash
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
JOURNEY_ROOMS_DIR="$ROOMS_DIR" JOURNEY_ASSETS_DIR="$ROOMS_DIR/assets" JOURNEY_SAVE_DIR="$ROOMS_DIR/save" \
  JOURNEY_SHARE_PORT=1 npx tsx ./server/canvas-server.ts >"$LOG" 2>&1 &
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
const document = doc.snapshot.documents.find((d) => d.state.typeName === 'document')?.state
if (document?.name !== model.title) {
  console.error(`FAIL: expected journey title ${JSON.stringify(model.title)}, got ${JSON.stringify(document?.name)}`)
  process.exit(1)
}
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

# No tunnel is ever opened here: POST /tunnel is asserted against a front-end that is down.
ASSETS_DIR="$ROOMS_DIR/assets"
SAVE_DIR="$ROOMS_DIR/save"
mkdir -p "$SAVE_DIR"
printf 'not really a png' >"$ROOMS_DIR/probe.bin"

curl -sf -X PUT -H 'Content-Type: image/png' --data-binary "@$ROOMS_DIR/probe.bin" \
  "http://127.0.0.1:$PORT/uploads/deep%2Fprobe.png" >/dev/null || { echo "FAIL: upload rejected"; exit 1; }
TYPE=$(curl -sf -o "$ROOMS_DIR/probe.back" -w '%{content_type}' "http://127.0.0.1:$PORT/uploads/deep%2Fprobe.png")
cmp -s "$ROOMS_DIR/probe.bin" "$ROOMS_DIR/probe.back" || { echo "FAIL: asset came back different"; exit 1; }
[ "$TYPE" = "image/png" ] || { echo "FAIL: asset lost its content type, got $TYPE"; exit 1; }
[ -f "$ASSETS_DIR/deep_probe.png" ] || { echo "FAIL: a slash in the id escaped the asset directory"; exit 1; }
echo "ok  asset round trip"

EMPTY=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
  -d '{"name":"empty.tldr","file":"{\"schema\":{},\"records\":[]}"}' "http://127.0.0.1:$PORT/save")
[ "$EMPTY" = "400" ] || { echo "FAIL: an empty board was accepted for saving, got $EMPTY"; exit 1; }
curl -sf -X POST -H 'Content-Type: application/json' \
  -d '{"name":"../../escape.tldr","file":"{\"schema\":{},\"records\":[{\"id\":\"x\",\"typeName\":\"page\"}]}"}' \
  "http://127.0.0.1:$PORT/save" >/dev/null || { echo "FAIL: save rejected a valid board"; exit 1; }
[ -f "$SAVE_DIR/escape.tldr" ] || { echo "FAIL: a traversing name escaped the save directory"; exit 1; }
echo "ok  save confined"

curl -sf "http://127.0.0.1:$PORT/tunnel" | grep -q '"running":false' || { echo "FAIL: a tunnel is reported before one was asked for"; exit 1; }
GUARD=$(curl -s -o /dev/null -w '%{http_code}' -X POST "http://127.0.0.1:$PORT/tunnel")
[ "$GUARD" = "409" ] || { echo "FAIL: expected 409 with no share front-end running, got $GUARD"; exit 1; }
echo "ok  tunnel refuses a missing front-end"
