#!/bin/sh
# Verifies — and best-effort repairs — kc-hyperfocus's MCP-server runtime
# dependencies after `bun install`.
#
# The hard dependency that breaks plugin installs in practice is `sharp`'s
# native binary, pulled by `@xenova/transformers`. sharp ships its actual
# `.node` artifact via `prebuild-install` in its postinstall hook. bun >= 1.0
# blocks transitive lifecycle scripts unless listed in `trustedDependencies`
# (this package.json lists sharp + onnxruntime-node) — but Claude Code's
# plugin-install pipeline does not always rerun `bun install` against the
# cached copy, so the prebuild-install step can still be skipped silently.
# When that happens the MCP server crashes on first import with:
#   "Cannot find module '../build/Release/sharp-darwin-arm64v8.node'"
#
# This script:
#   1. Probes whether sharp resolves and loads.
#   2. If not, runs sharp's own `prebuild-install` to download the
#      platform-specific binary. (Self-heal.)
#   3. Re-probes; reports OK or warns with actionable next steps.
#
# Exit policy: postinstall mode always exits 0 — a missing sharp degrades
# only the embedding tools (fuzzy semantic search). FTS5 search, insights,
# journal, and statusline keep working because lib/embeddings.ts loads
# @xenova/transformers via dynamic import (v1.6.3+). CI can set
# KC_HYPERFOCUS_VERIFY_STRICT=1 to treat the probe as a hard failure.

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PLUGIN_DIR" || exit 0

# ─── Ensure bun is reachable ────────────────────────────────────
export PATH="$HOME/.bun/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
if ! command -v bun >/dev/null 2>&1; then
  cat >&2 <<EOF
[kc-hyperfocus verify] WARN: bun not found on PATH; skipping load check.
The MCP server requires bun at runtime — install from https://bun.sh.
EOF
  if [ "${KC_HYPERFOCUS_VERIFY_STRICT:-}" = "1" ]; then
    echo "[kc-hyperfocus verify] FAIL: strict mode enabled; bun must be reachable." >&2
    exit 1
  fi
  exit 0
fi

# ─── probe_sharp: returns 0 if sharp loads, non-zero otherwise ──
probe_sharp() {
  bun -e "import('sharp').then(() => process.exit(0)).catch(e => { console.error(e?.message || e); process.exit(1); })" 2>"$1"
}

# ─── First probe ────────────────────────────────────────────────
ERR_FILE="$(mktemp)"
if probe_sharp "$ERR_FILE"; then
  rm -f "$ERR_FILE"
  echo "[kc-hyperfocus verify] OK — sharp native binary loadable."
  exit 0
fi

INITIAL_ERR="$(cat "$ERR_FILE")"
rm -f "$ERR_FILE"

# ─── Self-heal: run sharp's prebuild-install if available ───────
SHARP_DIR="$PLUGIN_DIR/node_modules/sharp"
if [ -d "$SHARP_DIR" ]; then
  echo "[kc-hyperfocus verify] sharp not loadable — attempting self-heal via bun install --force..." >&2

  # Self-heal strategy:
  #   1. `bun install --force` — most reliable: rebuilds both
  #      sharp/build/Release/*.node AND sharp/vendor/<libvips>/. Standalone
  #      prebuild-install only restores the .node and leaves vendor empty,
  #      so sharp still fails to load (Library not loaded: libvips-cpp).
  #   2. prebuild-install — fallback if bun install can't be re-run.
  #   3. install/check.js — last-resort heuristic.
  HEAL_LOG="$(mktemp)"
  HEAL_OK=0

  (cd "$PLUGIN_DIR" && bun install --force) >"$HEAL_LOG" 2>&1 && HEAL_OK=1

  if [ "$HEAL_OK" -eq 0 ] && [ -x "$PLUGIN_DIR/node_modules/.bin/prebuild-install" ]; then
    (cd "$SHARP_DIR" && "$PLUGIN_DIR/node_modules/.bin/prebuild-install") >>"$HEAL_LOG" 2>&1 && HEAL_OK=1
  fi

  if [ "$HEAL_OK" -eq 0 ] && [ -f "$SHARP_DIR/install/check.js" ]; then
    (cd "$SHARP_DIR" && bun run install/check.js) >>"$HEAL_LOG" 2>&1 && HEAL_OK=1
  fi

  HEAL_OUTPUT="$(cat "$HEAL_LOG")"
  rm -f "$HEAL_LOG"

  # Re-probe regardless of heal step exit code — what matters is the result.
  ERR_FILE="$(mktemp)"
  if probe_sharp "$ERR_FILE"; then
    rm -f "$ERR_FILE"
    echo "[kc-hyperfocus verify] OK — self-heal restored sharp."
    exit 0
  fi
  RECHECK_ERR="$(cat "$ERR_FILE")"
  rm -f "$ERR_FILE"

  cat >&2 <<EOF
[kc-hyperfocus verify] WARN: self-heal could not restore sharp.

Self-heal output:
$HEAL_OUTPUT

Re-probe error:
$RECHECK_ERR
EOF
else
  cat >&2 <<EOF
[kc-hyperfocus verify] WARN: sharp not loadable, and node_modules/sharp is missing.

Initial error:
$INITIAL_ERR
EOF
fi

cat >&2 <<EOF

What this means for you:
- The MCP server WILL still start (v1.6.3+ uses lazy import).
- FTS5 search, insights cache, journal entries, and statusline keep working.
- Only the embedding-based fuzzy semantic search will fail until sharp is fixed.

To fix manually:
  cd $PLUGIN_DIR
  rm -rf node_modules bun.lock
  bun install

If the error mentions libvips, install the system library first:
  macOS:    brew install vips
  Ubuntu:   apt-get install libvips-dev
  Fedora:   dnf install vips-devel
  Alpine:   apk add vips-dev

If problems persist, file an issue with this script's output:
  https://github.com/iamcxa/kc-claude-plugins/issues
EOF

if [ "${KC_HYPERFOCUS_VERIFY_STRICT:-}" = "1" ]; then
  echo "[kc-hyperfocus verify] FAIL: strict mode enabled; sharp must be loadable." >&2
  exit 1
fi

exit 0
