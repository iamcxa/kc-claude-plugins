#!/usr/bin/env bash
set -euo pipefail
# Prerequisites: Python 3, Git, tar, and this existing checkout with the named commit.
# No graphical surface changes. This checks the real local CLI with repository fixtures;
# it does not establish GitHub review, CI, gate approval, merge, or publication.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-ignores-url-paths-and-data-fences'
HEAD_SHA=6f2fe8f33de15cf4e9283bf9dfed185a5691ed57
BASE_SHA=e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e
export TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1

# 1. Export the exact candidate. Expected: candidate 6f2fe8f33de15cf4e9283bf9dfed185a5691ed57.
test "$(git -C "$WT" rev-parse "$HEAD_SHA")" = "$HEAD_SHA"
VALIDATION_EXPORT=$(mktemp -d /tmp/pr818-acceptance-XXXXXX)
git -C "$WT" archive "$HEAD_SHA" | tar -x -C "$VALIDATION_EXPORT"
printf 'candidate %s\n' "$HEAD_SHA"
cd "$VALIDATION_EXPORT/kc-dev-flow-2/scripts"

# 2. Exercise the five original inputs through question. Expected: five exit 0 / gate text complete lines.
python3 -B - <<'PY'
import test_delivery_gate as t
q=t.QuestionTests()
cases=[
    ("site paths", "`fix(relay): /llms.txt teaches agents` `/web/favicon.svg` `/pair`", {}),
    ("elided package", "`python3 .../scripts/adr_lint.py docs/adr --since a3f28ef6`", {}),
    ("namespace", "`{http://www.w3.org/2000/svg}svg`", {"task":t.TASK+"\n## Stage Report: validation\n`{http://www.w3.org/2000/svg}svg`"}),
    ("design YAML", "Review this candidate.", {"summary":"Read design/built-review.md", "cards":{"design/built-review.md":"```yaml\ndesign_review:\n  adrs_read:\n    - docs/adr/0064-the-first-screen-leads-with-sign-in.md (Accepted)\n```\n"}}),
    ("review YAML", "Review this candidate.", {"summary":"Read review/chief-engineer-1.md", "cards":{"review/chief-engineer-1.md":"```yaml\nchief_engineer_advice:\n  outcome: A Pilot stage dispatch records its actual inputs in the stamp commit.\n```\n"}}),
]
for name,text,kw in cases:
    code,out=q.ask(text,cli=True,**kw)
    assert code==0 and "gate text complete" in out, (name,code,out)
    print(name+": exit 0 / gate text complete")
PY

# 3. Verify the retained holds and the seven reverse mutations. Expected: Ran 7 tests, OK (no skips).
python3 -B -m unittest -v \
  test_delivery_gate.CaptainStepsTests.test_site_and_elided_paths_are_not_files_without_a_real_top_level_directory \
  test_delivery_gate.CaptainStepsTests.test_braced_namespace_uri_is_not_a_link_but_plain_urls_still_hold \
  test_delivery_gate.CaptainStepsTests.test_named_cards_require_shell_and_untagged_fences_but_skip_data \
  test_delivery_gate.CaptainStepsTests.test_yaml_message_and_missing_paths_keep_their_holds \
  test_delivery_gate.CaptainStepsTests.test_non_shell_fences_need_a_recorded_step_unless_they_match_observed \
  test_delivery_gate.QuestionTests.test_question_keeps_yaml_fences_in_the_report_as_steps \
  test_delivery_gate.QuestionTests.test_question_accepts_named_yaml_cards_and_holds_real_steps_and_paths

# 4. Check the exact file boundary and unchanged workflow. Expected: scope and workflow unchanged; PASS.
git -C "$WT" diff --name-only "$BASE_SHA" "$HEAD_SHA" > "$VALIDATION_EXPORT/changed.txt"
python3 -B - "$VALIDATION_EXPORT/changed.txt" <<'PY'
from pathlib import Path
import sys
assert Path(sys.argv[1]).read_text().splitlines()==[
    "kc-dev-flow-2/scripts/delivery_gate.py",
    "kc-dev-flow-2/scripts/test_delivery_gate.py"]
PY
git -C "$WT" show "$BASE_SHA:kc-dev-flow-2/references/sd/workflow.md" > "$VALIDATION_EXPORT/workflow-base.md"
cmp "$VALIDATION_EXPORT/workflow-base.md" "$VALIDATION_EXPORT/kc-dev-flow-2/references/sd/workflow.md"
printf 'scope and workflow unchanged\nPASS\n'

