#!/usr/bin/env bash
# version-parity-check.sh — Assert version parity across every source for each
# marketplace plugin:
#
#   plugin.json (canonical)  ==  marketplace.json entry
#                            ==  .codex-plugin/plugin.json (if present)
#                            ==  README badge  (### [<plugin>](...) `vX.Y.Z`)
#
# Why this exists: a version bump that updates `plugin.json` but silently skips
# `marketplace.json`, the README badge, or the Codex manifest ships a
# half-published version. The kc-marketplace-sync Steps 1.5 (codex drift) and 2
# (marketplace + README) are prose-level and easy to miss; this is the
# machine-enforced backstop. Cheap by design — python3 + grep only, no `claude`
# CLI, so it runs on every PR.
#
# Usage: ./scripts/version-parity-check.sh
# Exit 0 = all plugins consistent; exit 1 = at least one mismatch.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MARKETPLACE_JSON="$REPO_DIR/.claude-plugin/marketplace.json"
README="$REPO_DIR/README.md"

manifest_ver () { python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['version'])" "$1"; }

PLUGINS=$(python3 -c "import json; [print(p['name']) for p in json.load(open('$MARKETPLACE_JSON'))['plugins']]")

FAIL=0
printf "%-18s %-9s %-9s %-9s %-9s %s\n" PLUGIN plugin.json market codex README RESULT
for P in $PLUGINS; do
  PJ=$(manifest_ver "$REPO_DIR/$P/.claude-plugin/plugin.json")
  MK=$(python3 -c "import json,sys; print(next((p.get('version','') for p in json.load(open(sys.argv[1]))['plugins'] if p['name']==sys.argv[2]), ''))" "$MARKETPLACE_JSON" "$P")
  # Only check the Codex manifest if it is git-tracked (or staged). Untracked
  # local .codex-plugin/ files exist on some dev machines but are not shipped;
  # gating on tracked-state keeps local runs consistent with a clean CI checkout.
  if git -C "$REPO_DIR" ls-files --error-unmatch "$P/.codex-plugin/plugin.json" >/dev/null 2>&1; then
    CX=$(manifest_ver "$REPO_DIR/$P/.codex-plugin/plugin.json")
  else
    CX="-"
  fi
  RM=$(grep -E "^### \[$P\]" "$README" | grep -oE '`v[0-9]+\.[0-9]+\.[0-9]+`' | head -1 | tr -d '`v')
  RM="${RM:-<none>}"

  MISMATCH=""
  [ "$MK" != "$PJ" ] && MISMATCH="$MISMATCH marketplace.json=$MK"
  [ "$CX" != "-" ] && [ "$CX" != "$PJ" ] && MISMATCH="$MISMATCH codex=$CX"
  [ "$RM" != "$PJ" ] && MISMATCH="$MISMATCH README=$RM"

  if [ -n "$MISMATCH" ]; then
    printf "%-18s %-9s %-9s %-9s %-9s STALE (expect %s; got%s)\n" "$P" "$PJ" "$MK" "$CX" "$RM" "$PJ" "$MISMATCH"
    FAIL=1
  else
    printf "%-18s %-9s %-9s %-9s %-9s ok\n" "$P" "$PJ" "$MK" "$CX" "$RM"
  fi
done

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "Version parity: all plugins consistent"
  exit 0
else
  echo "Version parity: MISMATCH detected — bump every source to the plugin.json version"
  echo "(see kc-marketplace-sync Steps 1.5 codex-drift + 2 marketplace/README, and CLAUDE.md 'Version parity')"
  exit 1
fi
