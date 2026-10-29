#!/bin/bash
set -eu
# 1. Create an isolated checkout of the exact candidate. Expected: the full SHA below.
SOURCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-amendment-form-checked
STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
README=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/README.md
PACKAGE=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0
HEAD_SHA=da5053febb546b2a7cf6ffe676b0d5a8b7e338a4
BASE_SHA=5725d495bb83a17ec13616bb5421bf5ffdc71f70
RUN_DIR=$(mktemp -d /tmp/captain-amendment-acceptance.XXXXXX)
CHECKOUT="$RUN_DIR/code"
git -C "$SOURCE" worktree add --detach "$CHECKOUT" "$HEAD_SHA"
cleanup() { cd /tmp; git -C "$SOURCE" worktree remove "$CHECKOUT"; rmdir "$RUN_DIR"; }
trap cleanup EXIT
cd "$CHECKOUT"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$CHECKOUT" rev-parse HEAD
export PYTHONDONTWRITEBYTECODE=1
# 2. Check amendment forms and dispatch boundaries. Expected: 8 tests, OK.
(cd "$CHECKOUT/kc-dev-flow-2/scripts" && python3 -B -m unittest test_design_surfaces.AmendmentStructureTests test_dispatch_records.AmendmentDispatchFormTests)
# 3. Check committed edits, allowed appends, paths and missing evidence. Expected: 12 tests, OK.
(cd "$CHECKOUT/kc-dev-flow-2/scripts" && python3 -B -m unittest test_laws_check.L3Test)
# 4. Replay the three real rewrites, then lint ADRs. Expected: each exit=1 with an L3 violation; 42 ADR files, 0 legacy, exit=0.
for EVENT in 95fe8ce1bd7ff58798634b733abb4115fecfe23d 16129ea4c1a238dd885e9f08513ce3a52ad27f2d 34c820b5db98d5da119a1b021ce6af45d616acdc; do
  CODE=0
  OUTPUT=$(python3 -B "$CHECKOUT/kc-dev-flow-2/scripts/laws_check.py" "$STATE" --before "$EVENT^" --after "$EVENT" --readme "$README") || CODE=$?
  printf '%s\nexit=%s\n' "$OUTPUT" "$CODE"
  test "$CODE" = 1
  printf '%s\n' "$OUTPUT" | grep -q 'violation: L3 amendment-append-only'
done
python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA"
printf 'adr_lint exit=0\n'
# 5. Confirm candidate unchanged and remove only this checkout. Expected: PASS and no retained checkout.
test -z "$(git -C "$CHECKOUT" status --porcelain)"
cleanup
trap - EXIT
printf 'PASS: acceptance complete; temporary checkout removed\n'
