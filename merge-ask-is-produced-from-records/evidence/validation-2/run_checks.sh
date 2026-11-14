#!/usr/bin/env bash
set -u
R=/tmp/dev2/kc-claude-plugins-3042bb224e995ded/merge-ask-is-produced-from-records/validation-2
export PRODUCT_WORKTREE="$R/candidate" SOURCE_REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-ask-is-produced-from-records
export STATE_ROOT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
export SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock PROBE_RUN=repair-final- TMPDIR="$R/tmp" PYTHONDONTWRITEBYTECODE=1
cd "$R/candidate" || exit 1
run_probe() { python3 -B "$R/$1" "${@:2}" > "$R/results/${1%.py}${2:+-$2}.log" 2>&1; printf '%s %s exit=%s\n' "$1" "${2:-}" "$?"; }
bash --noprofile --norc "$R/acceptance.sh" > "$R/results/acceptance.log" 2>&1
printf 'acceptance exit=%s\n' "$?"
run_probe contract_forms_probe.py
run_probe visibility_probe.py
run_probe round2_probe.py replay
run_probe round2_probe.py rounds
run_probe goal_and_mutation.py
run_probe candidate_mutations.py
run_probe shared_guards.py
run_probe mutations.py
run_probe contract_mutations.py
run_probe late_head.py
