#!/bin/bash
set -euo pipefail
# Step 1 — isolate the exact candidate. Expected: STEP 1 PASS with the full SHA.
export PR770_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-rewritten-criteria-checked-against-captain-words'
export PR770_STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
export PR770_HEAD=b81c628facd2cd38568018beec47b6c4566c0aae
export PR770_BASE=2bda2e98304261d46b0ae7205a29ddc9038d2b4d
export PR770_RUN
PR770_RUN=$(mktemp -d "$PR770_SOURCE/.context/pr770-acceptance.XXXXXX")
export PR770_FIXTURE
PR770_FIXTURE=$(mktemp -d /tmp/pr770-acceptance.XXXXXX)
cleanup() {
  if test -e "$PR770_RUN/candidate/.git"; then
    git -C "$PR770_SOURCE" worktree remove "$PR770_RUN/candidate"
  fi
  rm -rf "$PR770_RUN" "$PR770_FIXTURE"
}
trap cleanup EXIT
git -C "$PR770_SOURCE" worktree add --detach "$PR770_RUN/candidate" "$PR770_HEAD"
test "$(git -C "$PR770_RUN/candidate" rev-parse HEAD)" = "$PR770_HEAD"
test -z "$(git -C "$PR770_RUN/candidate" status --porcelain)"
echo "STEP 1 PASS: $PR770_HEAD"

# Step 2 — replay the historical widening and deletion control. Expected: raw 1/1 with one candidate-only 41-word diagnostic; normalized 0/1; deletion 0/0.
mkdir "$PR770_RUN/base"
git -C "$PR770_SOURCE" archive "$PR770_BASE" kc-dev-flow-2 | tar -x -C "$PR770_RUN/base"
git -C "$PR770_STATE" archive b4e88ece4 peer-status-reaches-fresh.md peer-status-reaches-fresh/dispatch | tar -x -C "$PR770_FIXTURE"
python3 -B - <<'PY'
import os,subprocess
from pathlib import Path
root=Path(os.environ['PR770_RUN']); fixture=Path(os.environ['PR770_FIXTURE'])
record=fixture/'peer-status-reaches-fresh/dispatch/validation-2.md'
task=fixture/'peer-status-reaches-fresh.md'
def check(side):
    return subprocess.run(['python3','-B',str(root/side/'kc-dev-flow-2/scripts/dispatch_records.py'),'--names','--strict',str(record)],capture_output=True,text=True)
a,b=check('base'),check('candidate')
assert (a.returncode,b.returncode)==(1,1)
assert a.stdout=='' and a.stderr==b.stderr and "no 'Symptom:' line" in a.stderr
assert len(b.stdout.splitlines())==1 and 'AC-9 (Captain amendment 3)' in b.stdout and 'words: revision, link;' in b.stdout
assert len(b.stdout.split(':1: ',1)[1].split())==41
print('STEP 2 raw PASS: base=1 candidate=1; shared Symptom hint; candidate-only revision, link; 41 words')
record.write_text('Symptom: none\n'+record.read_text())
a,b=check('base'),check('candidate')
assert (a.returncode,a.stdout,a.stderr)==(0,'','') and b.returncode==1 and b.stderr==''
assert 'words: revision, link;' in b.stdout
print('STEP 2 normalized PASS: base=0 candidate=1; widening held')
task.write_text(task.read_text().replace('include source revision/link.','include source.'))
for side in ('base','candidate'):
    r=check(side)
    assert (r.returncode,r.stdout,r.stderr)==(0,'','')
print('STEP 2 deletion PASS: base=0 candidate=0; both silent')
PY

# Step 3 — exercise controls, repair dispatches, Symptom integration and event-time classification. Expected: Ran 23 tests, OK.
(cd "$PR770_RUN/candidate/kc-dev-flow-2/scripts" && python3 -B -m unittest test_design_surfaces.AddedWordsTests test_dispatch_records.RewrittenCriterionTests test_dispatch_records.SymptomDispatchTests test_laws_check.L2Test.test_rewritten_criterion_is_an_event_violation_and_later_clearance_is_not_retroactive -q)
echo 'STEP 3 PASS: comparison, Symptom and event-time checks'

# Step 4 — check unchanged workflow words and decision record. Expected: 5836 words; lint passes; 53 ADR files, 0 legacy.
cmp "$PR770_RUN/base/kc-dev-flow-2/references/sd/workflow.md" "$PR770_RUN/candidate/kc-dev-flow-2/references/sd/workflow.md"
test "$(wc -w < "$PR770_RUN/candidate/kc-dev-flow-2/references/sd/workflow.md" | tr -d ' ')" = 5836
(cd "$PR770_RUN/candidate" && python3 -B kc-dev-flow-2/scripts/lint-skills.py)
(cd "$PR770_RUN/candidate" && python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since "$PR770_BASE" --require 0057)
git -C "$PR770_RUN/candidate" diff --check "$PR770_BASE" "$PR770_HEAD"
echo 'STEP 4 PASS: workflow unchanged at 5836 words; lint and ADR checks passed'

# Step 5 — verify unchanged product and remove the scratch worktree. Expected: STEP 5 PASS.
test -z "$(git -C "$PR770_RUN/candidate" status --porcelain)"
cleanup
trap - EXIT
test ! -e "$PR770_RUN"
test ! -e "$PR770_FIXTURE"
echo 'STEP 5 PASS: product clean; temporary worktree and fixtures removed'

