#!/usr/bin/env bash
set -euo pipefail
# No graphical UI is changed. Requires git, tar, Python 3.10+, and the assigned repository with both pinned commits.
# Run: bash --noprofile --norc /absolute/path/to/validation-1/acceptance.sh /absolute/path/to/assigned/repository
# This checks local command behavior and scope, not hosted merge, release, adoption, or reviewer independence.
REPO=${1:?Pass the assigned repository path}
EVIDENCE=$(cd "$(dirname "$0")" && pwd)
HEAD_SHA=2a72c89b9aa9d114e45aeb16b746b8ca9f747bb8
BASE_SHA=6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1
SCRATCH=$(mktemp -d /tmp/pr825-acceptance.XXXXXX)
trap 'rm -rf "$SCRATCH"' EXIT
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
export PYTHONDONTWRITEBYTECODE=1
# Step 1: Export exact commits. Expected: STEP 1 PASS; no repository worktree/config changes.
mkdir "$SCRATCH/candidate" "$SCRATCH/base" "$SCRATCH/results"
git -C "$REPO" archive "$HEAD_SHA" | tar -x -C "$SCRATCH/candidate"
git -C "$REPO" archive "$BASE_SHA" | tar -x -C "$SCRATCH/base"
printf '%s\n' 'STEP 1 PASS: exact candidate and base exported.'
# Step 2: Run both real CLI routes. Expected: 44 paired runs pass and counterexamples are caught.
python3 -B "$EVIDENCE/route-probes.py" "$SCRATCH/candidate" "$SCRATCH/base" "$SCRATCH/results"
printf '%s\n' 'STEP 2 PASS: attribution allowed; unrecorded Captain links held; recorded links allowed.'
# Step 3: Run the seven new tests and two unchanged link-boundary tests. Expected: Ran 9 tests; OK.
(cd "$SCRATCH/candidate/kc-dev-flow-2/scripts" && python3 -B -m unittest -q \
  test_delivery_gate.CaptainStepsTests.test_pr_body_attribution_line_needs_no_recorded_link_step \
  test_delivery_gate.CaptainStepsTests.test_attribution_url_elsewhere_needs_a_recorded_link_step \
  test_delivery_gate.CaptainStepsTests.test_attribution_line_with_more_text_keeps_its_links \
  test_delivery_gate.CaptainStepsTests.test_pr_body_other_url_still_needs_a_recorded_link_step \
  test_delivery_gate.CaptainStepsTests.test_attribution_exemption_falsifiers \
  test_delivery_gate.TaskFolderCaptainTests.test_question_pr_body_attribution_line_needs_no_recorded_link_step \
  test_delivery_gate.TaskFolderCaptainTests.test_question_named_captain_link_holds_until_recorded \
  test_delivery_gate.CaptainStepsTests.test_named_card_prose_link_matches_asked_and_holds_when_unrecorded \
  test_delivery_gate.TaskFolderCaptainTests.test_report_only_cards_require_fences_and_fo_named_cards_also_require_links)
printf '%s\n' 'STEP 3 PASS: nine regression and boundary tests.'
# Step 4: Check exact file scope and unchanged startup documents. Expected: two files; help 1214 -> 1225; extra-file falsifier caught.
python3 - "$REPO" "$BASE_SHA" "$HEAD_SHA" "$SCRATCH" <<'PY'
from pathlib import Path
import subprocess,sys
repo,base,head,tmp=sys.argv[1:]
expected={'kc-dev-flow-2/scripts/delivery_gate.py','kc-dev-flow-2/scripts/test_delivery_gate.py'}
changed=set(subprocess.check_output(['git','-C',repo,'diff','--name-only',base,head],text=True).splitlines())
assert changed==expected,changed
assert changed | {'kc-dev-flow-2/README.md'} != expected
subprocess.run(['git','-C',repo,'diff','--check',base,head],check=True)
roots=[Path(tmp)/'base',Path(tmp)/'candidate']
for path in ['kc-dev-flow-2/README.md','kc-dev-flow-2/references/sd/workflow.md']:
    assert (roots[0]/path).read_bytes()==(roots[1]/path).read_bytes(),path
words=[len(subprocess.check_output([sys.executable,'-B',str(root/'kc-dev-flow-2/scripts/delivery_gate.py'),'--help'],text=True).split()) for root in roots]
assert words==[1214,1225],words
assert 'nor is a line that is only the Claude Code attribution' in (roots[1]/'kc-dev-flow-2/scripts/delivery_gate.py').read_text()
print('STEP 4 PASS: exactly two files; startup bytes unchanged; help 1214 -> 1225 words; extra-file falsifier caught.')
PY
printf '%s\n' 'ACCEPTANCE PASSED at 2a72c89b9aa9d114e45aeb16b746b8ca9f747bb8'
