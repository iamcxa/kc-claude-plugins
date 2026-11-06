#!/bin/bash
set -euo pipefail
# Prerequisites: this clone, its shared state checkout, Python 3, Git, tar, bash,
# and the declared kc-dev-flow-2 0.35.0 package. No visible UI changes.
# Run unchanged with: bash --noprofile --norc /absolute/path/to/acceptance.sh

# 1. Export the exact candidate and base; expect Candidate: 5b3e290a... .
repo=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-question-requires-worktree-clause
state=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
package=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0
head=5b3e290a7eaceb0fe70f489d25d622314598b9f0
base=b804d81d3abc94c9c321326dc75e7cac927c5252
verify=$(mktemp -d /tmp/delivery-clause-acceptance.XXXXXX)
mkdir -p "$verify/candidate" "$verify/base"
git -C "$repo" archive "$head" | tar -x -C "$verify/candidate"
git -C "$repo" archive "$base" | tar -x -C "$verify/base"
printf 'Candidate: %s\nExports: %s\n' "$head" "$verify"

# 2. Exercise the gate, summary-only clause, wording, and unchanged check.
# Expect: Ran 12 tests ... OK, including the keeping-worktree mutation.
(cd "$verify/candidate/kc-dev-flow-2/scripts" && python3 -B -m unittest -v test_delivery_gate.QuestionTests)

# 3. Replay actual recorded question strings through valid fixture tasks.
# Expect: candidate #786/#787/#788 exits 1/1/0; base exits 0/0/0.
python3 -B "$state/delivery-question-requires-worktree-clause/ideation/replay_question.py" "$verify/candidate" "$state"
python3 -B "$state/delivery-question-requires-worktree-clause/ideation/replay_question.py" "$verify/base" "$state"

# 4. Compare the merge-time check and retained workflow at the two revisions.
# Expect: check output identical, exit 0; workflow bytes identical.
python3 -B - "$verify/candidate" "$verify/base" <<'PY'
import sys, types
from pathlib import Path
candidate, baseline = map(Path, sys.argv[1:])
sys.path.insert(0, str(candidate / 'kc-dev-flow-2/scripts'))
import test_delivery_gate as t
path = baseline / 'kc-dev-flow-2/scripts/delivery_gate.py'
base_module = types.ModuleType('baseline_gate')
base_module.__file__ = str(path)
exec(compile(path.read_text(), str(path), 'exec'), base_module.__dict__)
question = t.QuestionTests.recorded_questions[786]
before, after = t.run_variant(base_module, text=question), t.run_check(text=question)
assert (before.code, before.out) == (after.code, after.out)
assert after.code == 0
print('check output identical, exit 0 (synthetic task and gh facts)')
PY
cmp "$verify/base/kc-dev-flow-2/references/sd/workflow.md" "$verify/candidate/kc-dev-flow-2/references/sd/workflow.md"
printf 'workflow bytes identical\n'

# 5. Check documentation and version integrity from the exported candidate.
# Git metadata is read-only; no new worktree or Git configuration is created.
# Expect: 61 ADR file(s) checked, 0 legacy; lint PASS, 5939 of 5939 words;
# Version parity: all plugins consistent; acceptance PASS. Every command exits 0.
cd "$verify/candidate"
gitdir=$(git -C "$repo" rev-parse --absolute-git-dir)
GIT_DIR="$gitdir" GIT_WORK_TREE="$verify/candidate" python3 -B "$package/scripts/adr_lint.py" docs/adr --since "$base" --require 0023 0044 0051 0062
python3 -B kc-dev-flow-2/scripts/lint-skills.py
GIT_DIR="$gitdir" GIT_WORK_TREE="$verify/candidate" bash scripts/version-parity-check.sh
printf 'acceptance PASS\n'
# Limits: synthetic gate task/gh facts isolate the real historical questions.
# This does not merge, remove worktrees, authorize delivery, check real cleanliness,
# run all package tests, or prove the Captain saw or approved the question.
