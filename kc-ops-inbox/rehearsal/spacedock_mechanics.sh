#!/usr/bin/env bash
# Exercise, with no hermes and no model, the spacedock steps the ops First Officer skill drives.
# usage: spacedock_mechanics.sh [SCRATCH_DIR]   (default: a new mktemp dir; removed on success)
set -euo pipefail
SD=${SPACEDOCK_BIN:-spacedock}
HERE=$(cd "$(dirname "$0")" && pwd)
S=${1:-$(mktemp -d)}
R=$S/repo
W=$R/docs/ops
SLUG=relay-bound-ceiling-near-2026-10-20
fail() { echo "FAIL: $*" >&2; exit 1; }

mkdir -p "$W" && cd "$R"
git init -q -b main && git config user.email rehearsal@example.invalid && git config user.name rehearsal
cp "$HERE/../ops-workflow/README.md" "$W/README.md"
echo "docs/ops/.spacedock-state/" > .gitignore
git add . && git commit -qm "ops workflow"
git worktree add -q --orphan -b spacedock-state/ops "$W/.spacedock-state"
"$SD" status --workflow-dir "$W" --validate | grep -q VALID || fail "workflow invalid"

printf -- '---\ntitle: relay ceiling near 40 of 50\nstatus: inbox\n---\n\n## Event\n\n## Diagnosis\n\n## Options\n\n## Recommendation\n' > "$S/body.md"
"$SD" new "$SLUG" --workflow-dir "$W" < "$S/body.md" >/dev/null
"$SD" state commit "$SLUG" --workflow-dir "$W" >/dev/null
"$SD" gate prepare "$SLUG" --workflow-dir "$W" --question "Which option?" \
  --artifact "$W/.spacedock-state/$SLUG.md" --summary "ceiling near" >/dev/null
"$SD" state commit "$SLUG" --workflow-dir "$W" >/dev/null
NEXT=$("$SD" status --workflow-dir "$W" --next --json)
echo "$NEXT" | grep -q '"readiness":"awaiting-captain"' || fail "gate not open: $NEXT"
echo "open gate, no reply: $NEXT"

COMMITS=$(git -C "$W/.spacedock-state" rev-list --count HEAD)
echo "state commits before any reply: $COMMITS"

"$SD" gate record "$SLUG" --workflow-dir "$W" --decision hold --actor person:captain --reason "hold, check tomorrow" | tail -1
grep -q 'by: person:captain' "$W/.spacedock-state/$SLUG.md" || fail "actor not recorded"
echo "recorded actor is a caller-supplied string: spacedock does not authenticate it"
echo "scratch kept at $S"
