#!/usr/bin/env bash
# No UI surface. This checks observable merge holds and records; it does not run
# the whole package suite or prove a live post-release merge ask.
set -euo pipefail
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-ask-tests-the-merge-result
EVIDENCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/merge-ask-tests-the-merge-result/validation
# 1. Export the exact candidate and base. Expect: exported candidate and base.
SCRATCH=$(mktemp -d /tmp/merge-result-853-acceptance.XXXXXX)
trap 'rm -rf "$SCRATCH"' EXIT
printf 'scratch: %s\n' "$SCRATCH"
mkdir "$SCRATCH/candidate" "$SCRATCH/base" "$SCRATCH/tmp"
git -C "$REPO" archive d79053d0836c558a9269f9cf1ba222933935b820 | tar -x -C "$SCRATCH/candidate"
git -C "$REPO" archive 8ce0eb6050c889b21baccf50fec35231bc888d66 | tar -x -C "$SCRATCH/base"
export TMPDIR="$SCRATCH/tmp" MERGE_REPLAY_CODE="$REPO" PYTHONDONTWRITEBYTECODE=1
GATE="$SCRATCH/candidate/kc-dev-flow-2/scripts/delivery_gate.py"
echo 'exported candidate and base'
# 2. Replay the historical ask. Expect: base=0; candidate=1, missing run.
python3 -B "$EVIDENCE/replay_841.py" "$SCRATCH/base/kc-dev-flow-2/scripts/delivery_gate.py" "$SCRATCH/base.log"
set +e
python3 -B "$EVIDENCE/replay_841.py" "$GATE" "$SCRATCH/held.log"
HELD=$?
set -e
test "$HELD" -eq 1
grep 'no merge-result run is recorded' "$SCRATCH/held.log"
echo 'base=0; candidate=1, missing run'
# 3. Read the independently rerun green record at each trunk. Expect: correct=0; stale=1.
python3 -B "$EVIDENCE/replay_841.py" "$GATE" "$SCRATCH/green.log" --result "$EVIDENCE/green-result-1.json" --trunk 546a136386c94c58e430c91a6f3457b38bd73880
set +e
python3 -B "$EVIDENCE/replay_841.py" "$GATE" "$SCRATCH/stale.log" --result "$EVIDENCE/green-result-1.json"
STALE=$?
set -e
test "$STALE" -eq 1
grep 'point: merge-result:' "$SCRATCH/green.log"
echo 'correct=0; stale=1'
# 4. Exercise runtime cleanup, mismatch, failure and question disclosure. Expect: 13 tests, OK.
(cd "$SCRATCH/candidate/kc-dev-flow-2/scripts" && python3 -B -m unittest test_delivery_gate.MergeResultTests test_delivery_gate.MergeRunTests test_delivery_gate.DeliveryCheckBeforeQuestionTests.test_not_run_line_must_be_in_the_question_itself)
echo 'Acceptance PASS'
