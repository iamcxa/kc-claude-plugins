#!/bin/sh
# Verifies that kc-hyperfocus's MCP-server dependencies are loadable
# after `bun install`.
#
# Why this exists: bun >= 1.0 blocks postinstall scripts of dependencies
# unless they're listed in the consumer's `trustedDependencies` array.
# @xenova/transformers transitively requires `sharp`, which uses
# `prebuild-install` in its postinstall to download a platform-specific
# native binary. Without trusted-deps coverage, the install reports
# success but the binary is missing, and the first `import` at runtime
# crashes with an opaque ENOENT or "Cannot find module" error.
#
# This script runs as kc-hyperfocus's own postinstall hook. It exercises
# the import path that the MCP server itself takes, so any deferred
# failure surfaces here instead of at first MCP tool call.
#
# Exit policy: always exit 0. A failed import warns loudly but does NOT
# block install — text-only embedding workflows may still function if
# the user does not use the image-processing code paths. Hard-failing
# would prevent install on platforms where sharp's prebuilt binary is
# legitimately unavailable (some Alpine variants, etc.).

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PLUGIN_DIR" || exit 0

# ─── Ensure bun is reachable ────────────────────────────────────
export PATH="$HOME/.bun/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
if ! command -v bun >/dev/null 2>&1; then
  cat >&2 <<EOF
[kc-hyperfocus verify] WARN: bun not found on PATH; skipping load check.
The MCP server requires bun at runtime — install from https://bun.sh.
EOF
  exit 0
fi

# ─── Probe @xenova/transformers import ───────────────────────────
ERR_FILE="$(mktemp)"
if bun -e "import('@xenova/transformers').then(() => process.exit(0)).catch(e => { console.error(e?.message || e); process.exit(1); })" 2>"$ERR_FILE"; then
  rm -f "$ERR_FILE"
  echo "[kc-hyperfocus verify] OK — embedding deps loadable."
  exit 0
fi

ERR_MSG="$(cat "$ERR_FILE")"
rm -f "$ERR_FILE"

cat >&2 <<EOF
[kc-hyperfocus verify] WARN: @xenova/transformers failed to import.

Underlying error:
$ERR_MSG

Most common cause: bun blocked sharp's postinstall (prebuild-install),
so its native binary was never downloaded. This package.json already
lists "sharp" in trustedDependencies; if you're seeing this anyway:

  cd $PLUGIN_DIR
  rm -rf node_modules bun.lock
  bun install

If the error mentions libvips, install the system library:
  macOS:    brew install vips
  Ubuntu:   apt-get install libvips-dev
  Fedora:   dnf install vips-devel
  Alpine:   apk add vips-dev

If problems persist on this platform, the kc-hyperfocus journal-search
MCP tools will not work until resolved. The plugin's skills and hooks
themselves continue to function. File an issue at:
  https://github.com/iamcxa/kc-claude-plugins/issues

Install will continue; this is a warning, not a fatal error.
EOF

exit 0
