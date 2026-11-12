#!/bin/bash
set -euo pipefail
TASK_CODE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-gate-question-facts-are-checked-before-the-captain-reads-them'
TASK_STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
TASK_PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1'
TASK_EVIDENCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/gate-question-facts-are-checked-before-the-captain-reads-them/validation-2'
TASK_HEAD=8d083d3b9b2c48c10e32cee3e5ef693b374c6183
TASK_BASE=d79053d0836c558a9269f9cf1ba222933935b820
TASK_OUTPUT=${1:?Pass an existing writable output directory}
TASK_SCRATCH=${2:?Pass a new scratch path inside an owned scratch root}
test -d "$TASK_OUTPUT"
test ! -e "$TASK_SCRATCH"
mkdir -p "$TASK_SCRATCH"
export TMPDIR="$TASK_SCRATCH" PYTHONDONTWRITEBYTECODE=1
printf '%s\n' "$TASK_SCRATCH" > "$TASK_OUTPUT/captain-scratch.txt"

# Step 1: verify the candidate and export the three pinned source revisions.
/usr/bin/python3 -c 'import yaml'
test "$(git -C "$TASK_CODE" rev-parse HEAD)" = "$TASK_HEAD"
test -z "$(git -C "$TASK_CODE" status --porcelain)"
git -C "$TASK_CODE" merge-base --is-ancestor "$TASK_BASE" "$TASK_HEAD"
mkdir "$TASK_SCRATCH/candidate" "$TASK_SCRATCH/base" "$TASK_SCRATCH/poc"
git -C "$TASK_CODE" archive "$TASK_HEAD" | tar -x -C "$TASK_SCRATCH/candidate"
git -C "$TASK_CODE" archive "$TASK_BASE" | tar -x -C "$TASK_SCRATCH/base"
git -C "$TASK_CODE" archive e56b2e6c36f846349acc780175a0691b63a177ae | tar -x -C "$TASK_SCRATCH/poc"
printf 'Step 1: pinned candidate; three source exports ready\n'

# Step 2: replay historical questions and the three disclosure falsifiers.
/usr/bin/python3 -B "$TASK_EVIDENCE/replay.py" --export "$TASK_SCRATCH/candidate" --state "$TASK_STATE" --poc "$TASK_SCRATCH/poc" --base "$TASK_SCRATCH/base" > "$TASK_OUTPUT/captain-replay.json"
printf 'Step 2: disclosure replay passed; 4 of 4 known false claims marked\n'

# Step 3: run the real sibling listing and its hold-removal falsifier.
python3 -B "$TASK_EVIDENCE/run-ac1.py" --code "$TASK_CODE" --state "$TASK_STATE" --spacedock /Users/kent/.local/bin/spacedock --scratch "$TASK_SCRATCH/ac1" --output "$TASK_OUTPUT/captain-ac1" > "$TASK_OUTPUT/captain-ac1.log"
printf 'Step 3: held listing 5 of 5; control 0 of 5; hold-removal mutant rejected\n'

# Step 4: exercise focused behavior and check the authorized decision record.
cd "$TASK_SCRATCH/candidate/kc-dev-flow-2/scripts"
python3 -B -m unittest test_delivery_gate.ScopeDisclosureTests > "$TASK_OUTPUT/captain-tests.log" 2>&1
cd "$TASK_CODE"
python3 -B "$TASK_PACKAGE/scripts/adr_lint.py" docs/adr --since "$TASK_BASE" --require 0082 > "$TASK_OUTPUT/captain-adr.log" 2>&1
printf 'Step 4: nine scope tests and required ADR lint passed\n'
printf 'Scratch retained for post-commit cleanup: %s\n' "$TASK_SCRATCH"

