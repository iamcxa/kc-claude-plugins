#!/bin/bash
set -euo pipefail
TASK_CODE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-gate-question-facts-are-checked-before-the-captain-reads-them
TASK_STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
TASK_PACKAGE=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1
TASK_EVIDENCE="$TASK_STATE/gate-question-facts-are-checked-before-the-captain-reads-them/validation-1"
TASK_BASE=d79053d0836c558a9269f9cf1ba222933935b820
TASK_HEAD=8d083d3b9b2c48c10e32cee3e5ef693b374c6183
TASK_OUTPUT=${1:?Pass an existing writable evidence directory}
test -d "$TASK_OUTPUT"
TASK_SCRATCH=$(mktemp -d /tmp/gate-facts-captain-XXXXXX)
trap 'rm -rf -- "$TASK_SCRATCH"' EXIT
export TMPDIR="$TASK_SCRATCH" PYTHONDONTWRITEBYTECODE=1

# Step 1: pin and export the candidate, prerequisite and prototype.
test "$(git -C "$TASK_CODE" rev-parse HEAD)" = "$TASK_HEAD"
test -z "$(git -C "$TASK_CODE" status --porcelain)"
git -C "$TASK_CODE" merge-base --is-ancestor "$TASK_BASE" "$TASK_HEAD"
mkdir "$TASK_SCRATCH/candidate" "$TASK_SCRATCH/base" "$TASK_SCRATCH/poc"
git -C "$TASK_CODE" archive "$TASK_HEAD" | tar -x -C "$TASK_SCRATCH/candidate"
git -C "$TASK_CODE" archive "$TASK_BASE" | tar -x -C "$TASK_SCRATCH/base"
git -C "$TASK_CODE" archive e56b2e6c36f846349acc780175a0691b63a177ae | tar -x -C "$TASK_SCRATCH/poc"
printf 'Step 1: pinned candidate and exported three revisions\n'

# Step 2: replay recorded questions, actual file writes and the four falsifiers.
python3 -B "$TASK_EVIDENCE/replay.py" --export "$TASK_SCRATCH/candidate" --base "$TASK_SCRATCH/base" --poc "$TASK_SCRATCH/poc" --state "$TASK_STATE" > "$TASK_OUTPUT/captain-replay.json"
printf 'Step 2: replay assertions passed; AC-1 dependent candidate remains NOT RUN\n'

# Step 3: exercise the nine owned behavior tests from exported candidate bytes.
cd "$TASK_SCRATCH/candidate/kc-dev-flow-2/scripts"
python3 -B -m unittest test_delivery_gate.ScopeDisclosureTests > "$TASK_OUTPUT/captain-tests.log" 2>&1
printf 'Step 3: nine scope tests passed\n'

# Step 4: inspect required decision records using pinned, clean repository metadata.
cd "$TASK_CODE"
python3 -B "$TASK_PACKAGE/scripts/adr_lint.py" docs/adr --since "$TASK_BASE" --require 0082 > "$TASK_OUTPUT/captain-adr.log" 2>&1
printf 'Step 4: required decision-record lint passed\n'
rm -rf -- "$TASK_SCRATCH"
test ! -e "$TASK_SCRATCH"
printf '%s\n' "$TASK_SCRATCH" > "$TASK_OUTPUT/captain-scratch-removed.txt"
printf 'Cleanup: acceptance scratch removed\n'
