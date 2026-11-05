#!/usr/bin/env bash
# Requirements: this repository checkout and its Git history, Python 3, Git, the declared installed package and state checkout.
# Scope: no graphical screen; exercises reminders, recorded merge instructions, five historical answers and ADR provenance structure.
# Does not cover live chat fidelity, model success rate, GitHub review/CI, merge or installation.
# Step 1: create a clean detached copy. Expected: HEAD is 73db59bef6d1327e8b8c810b4f57601664aee1ef.
set -euo pipefail
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-gate-presentation-asks-one-thing-plainly'
CHECK=$(mktemp -d "$WT/.captain-check.XXXXXX")
trap 'git -C "$WT" worktree remove "$CHECK"' EXIT
git -C "$WT" worktree add --detach "$CHECK" 73db59bef6d1327e8b8c810b4f57601664aee1ef
test "$(git -C "$CHECK" rev-parse HEAD)" = 73db59bef6d1327e8b8c810b4f57601664aee1ef
cd "$CHECK"
export PYTHONDONTWRITEBYTECODE=1
# Step 2: exercise quote, whitespace, pending, delegated and withdrawn approval paths. Expected: 7 tests, OK.
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_delivery_gate.py -k BoundApprovalTests -v
# Step 3: replay the five committed historical answers. Expected: 1 test, OK; saved results contain five cases.
export GATE_PRESENTATION_STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
export GATE_PRESENTATION_BASE=d37c6dc653e0f45d6ca630c2faa6121c0863a57e
GATE_PRESENTATION_EVIDENCE=$(mktemp -d /tmp/gate-presentation-acceptance.XXXXXX)
export GATE_PRESENTATION_EVIDENCE
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_delivery_gate.py -k HistoricalBoundQuestionTests -v
# Step 4: test reminder placement and nested quotes; check ADR 0060 and unchanged workflow. Expected: 4 tests, OK; 59 ADRs pass; cmp exits 0.
PYTHONPATH="$CHECK/kc-dev-flow-2/scripts" python3 -B -m unittest test_design_surfaces.AskFormTests test_decision_ledger.BoundQuestionTests -v
python3 -B '/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py' docs/adr --since d37c6dc653e0f45d6ca630c2faa6121c0863a57e --require 0060
git -C "$CHECK" show d37c6dc653e0f45d6ca630c2faa6121c0863a57e:kc-dev-flow-2/references/sd/workflow.md | cmp - kc-dev-flow-2/references/sd/workflow.md
# Step 5: remove the clean test copy. Expected: "acceptance PASS"; historical JSON remains at the printed path.
git -C "$CHECK" diff --exit-code
cd "$WT"
git -C "$WT" worktree remove "$CHECK"
trap - EXIT
printf 'acceptance PASS; five-case evidence: %s/historical-replays.json\n' "$GATE_PRESENTATION_EVIDENCE"

