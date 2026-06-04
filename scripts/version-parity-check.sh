#!/usr/bin/env bash
# version-parity-check.sh — Assert version parity across every source for each
# marketplace plugin:
#
#   plugin.json (canonical)  ==  marketplace.json entry
#                            ==  .codex-plugin/plugin.json (if present)
#
# Why this exists: release-please owns version propagation (it bumps plugin.json,
# the Codex manifest, and the marketplace.json entry together in its Release PR).
# This check is the machine-enforced backstop that those three stay consistent —
# it both catches accidental manual drift AND validates release-please's own
# output. Cheap by design — python3 only, no `claude` CLI, so it runs on every PR.
# (README no longer carries per-plugin version badges; nothing to check there.)
#
# Usage: ./scripts/version-parity-check.sh
# Exit 0 = all plugins consistent; exit 1 = at least one mismatch.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MARKETPLACE_JSON="$REPO_DIR/.claude-plugin/marketplace.json"

manifest_ver () { python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['version'])" "$1"; }

PLUGINS=$(python3 -c "import json; [print(p['name']) for p in json.load(open('$MARKETPLACE_JSON'))['plugins']]")

FAIL=0
printf "%-18s %-9s %-9s %-9s %s\n" PLUGIN plugin.json market codex RESULT
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
  MISMATCH=""
  [ "$MK" != "$PJ" ] && MISMATCH="$MISMATCH marketplace.json=$MK"
  [ "$CX" != "-" ] && [ "$CX" != "$PJ" ] && MISMATCH="$MISMATCH codex=$CX"

  if [ -n "$MISMATCH" ]; then
    printf "%-18s %-9s %-9s %-9s STALE (expect %s; got%s)\n" "$P" "$PJ" "$MK" "$CX" "$PJ" "$MISMATCH"
    FAIL=1
  else
    printf "%-18s %-9s %-9s %-9s ok\n" "$P" "$PJ" "$MK" "$CX"
  fi
done

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "Version parity: all plugins consistent"
  exit 0
else
  echo "Version parity: MISMATCH detected — plugin.json / marketplace.json / codex disagree"
  echo "(release-please normally keeps these in lockstep in its Release PR; a mismatch means a manual edit drifted or release-please mis-wrote — fix the outlier to match plugin.json)"
  exit 1
fi
