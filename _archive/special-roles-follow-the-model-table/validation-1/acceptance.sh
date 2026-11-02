#!/bin/bash
set -euo pipefail
# No graphical surface. Covers local rules, table/lint, POC derivation, ADRs, and unchanged release-walk code.
# Does not rerun native Claude settings, historical replay, full CI, hosted checks, or post-merge seed retirement.

# 1. Create a detached checkout of the assigned head. Expected: HEAD 562b1a87198d97bb2ae1d87b72884e390b20e146.
SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table'
HEAD_SHA=562b1a87198d97bb2ae1d87b72884e390b20e146
BASE_SHA=c129cb215c2630d08853eeffae0fd5a2ee7e40c6
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
VERIFY_ROOT="$(mktemp -d "$SOURCE/.acceptance-562b1a87.XXXXXX")"
rmdir "$VERIFY_ROOT"
git -C "$SOURCE" worktree add --detach "$VERIFY_ROOT" "$HEAD_SHA"
trap 'git -C "$SOURCE" worktree remove "$VERIFY_ROOT"' EXIT
cd "$VERIFY_ROOT"
test "$(git -C "$VERIFY_ROOT" rev-parse HEAD)" = "$HEAD_SHA"
printf 'STEP 1: exact candidate %s\n' "$HEAD_SHA"

# 2. Exercise role floors, dates, waivers, and both model families. Expected: 27 tests, OK.
(cd "$VERIFY_ROOT/kc-dev-flow-2/scripts" && python3 -B -m unittest test_role_triggers)
printf 'STEP 2: role checks passed\n'

# 3. Check table/agent drift and POC stage removal. Expected: lint passes; 47 and 9 tests, OK.
python3 -B "$VERIFY_ROOT/kc-dev-flow-2/scripts/lint-skills.py"
python3 -B "$VERIFY_ROOT/kc-dev-flow-2/scripts/test_lint_skills.py"
python3 -B "$VERIFY_ROOT/kc-dev-flow-2/scripts/test_poc_readme.py"
printf 'STEP 3: lint and derivation checks passed\n'

# 4. Validate changed decision records and reserved ADR 0049. Expected: 48 files, 0 legacy; exit 0.
python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0049
printf 'STEP 4: decision records passed\n'

# 5. Verify workflow wording and seven approved table rows. Expected: 5781 words; 1 implementation-family phrase; 0 all-workers phrases; all seven rows match.
python3 -B - <<'PY'
from pathlib import Path
import re,sys
root=Path.cwd()/'kc-dev-flow-2'
text=(root/'references/sd/workflow.md').read_text()
assert len(text.split())==5781
assert text.count('from implementation workers')==1
assert text.count('from all workers')==0
sys.path.insert(0,str(root/'scripts'))
import test_sd_dispatch as dispatch
assert dispatch.fix_gaps(dispatch.pinned_texts())['reviewer-record']==([],[])
table=(root/'references/model-roster.md').read_text().split('## Model table\n',1)[1].split('\n## ',1)[0]
rows=re.findall(r'^\| ([a-z-]+) \| ([^|]+?) \| ([^|]+?) \|$',table,re.M)
assert rows==[
 ('implementation','Sonnet / high','Sol / xhigh'),
 ('chief-engineer','Opus / xhigh','Astra / xhigh'),
 ('engineering-reviewer','Opus / xhigh','Astra / xhigh'),
 ('design-director','Sonnet / high','Sol / xhigh'),
 ('ideation','Opus / high','Astra / xhigh'),
 ('validation','Opus / high','Astra / xhigh'),
 ('observer','Sonnet / high','Sol / high')]
print('STEP 5: 5781 words; family phrases 1/0; seven rows match')
PY

# 6. Confirm the release-walk files and exact candidate remain unchanged. Expected: no diff; clean checkout.
git -C "$VERIFY_ROOT" diff --exit-code "$BASE_SHA" "$HEAD_SHA" -- kc-dev-flow-2/scripts/release_acceptance.py kc-dev-flow-2/extensions/release-acceptance
test -z "$(git -C "$VERIFY_ROOT" status --porcelain)"
printf 'STEP 6: release walk unchanged; candidate clean\n'

