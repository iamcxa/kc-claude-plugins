#!/usr/bin/env bash
set -euo pipefail
# Requires git, Python 3 with PyYAML, bash, and network access to this public repository.
# Creates its own scratch; needs no product checkout or earlier validation scratch.
scratch_parent=/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/validation-2
parent_created=0
if [ ! -d "$scratch_parent" ]; then parent_created=1; fi
mkdir -p "$scratch_parent"
run=$(mktemp -d "$scratch_parent/captain-accept.XXXXXX")
trap 'rm -rf "$run"; if [ "$parent_created" = 1 ]; then rmdir "$scratch_parent" 2>/dev/null || true; fi' EXIT
mkdir -p "$run/tmp"
export TMPDIR="$run/tmp" PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
head=45d5ebb9d24665c0904aca5412123a7224d056cc
base=88f86f2749dadb6f4ef0cf9aa089c1827096865b
echo 'STEP 1: fetch and verify the exact public candidate'
git init -q "$run/source"
git -C "$run/source" fetch -q --depth=4 https://github.com/iamcxa/kc-claude-plugins.git "$head"
git -C "$run/source" checkout -q --detach FETCH_HEAD
test "$(git -C "$run/source" rev-parse HEAD)" = "$head"
test "$(git -C "$run/source" rev-parse HEAD^^^)" = "$base"
mkdir "$run/candidate"
git -C "$run/source" archive "$head" | tar -x -C "$run/candidate"
export GIT_DIR="$run/source/.git" GIT_WORK_TREE="$run/candidate"
cd "$run/candidate"
echo "STEP 1 PASS: $head"
echo 'STEP 2: run package lint, its regression suite, and ADR checks'
python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$run/lint.log"
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py > "$run/lint-tests.log" 2>&1
python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since "$base" --require 0084
tail -5 "$run/lint-tests.log"
echo 'STEP 2 PASS: lint, regression suite, ADR 0084'
echo 'STEP 3: verify unchanged POC derivation and the approved word increase'
git -C "$run/source" show "$base:kc-dev-flow-2/references/sd/workflow.md" > "$run/base-workflow.md"
python3 -B - "$run/base-workflow.md" <<'PY3'
import sys
from pathlib import Path
sys.path.insert(0, 'kc-dev-flow-2/scripts')
from poc_readme import derive
old=Path(sys.argv[1]).read_text()
new=Path('kc-dev-flow-2/references/sd/workflow.md').read_text()
assert derive(old)==derive(new), 'POC changed'
assert (len(old.split()),len(new.split()))==(6033,6099)
print('STEP 3 PASS: POC equal; startup words 6033 -> 6099 (+66)')
PY3
echo 'STEP 4: check amended AC-10 and the explicit per-criterion wording'
python3 -B - "$run/lint.log" <<'PY4'
import re,sys
from pathlib import Path
out=Path(sys.argv[1]).read_text()
old=sum('repeats' in line for line in out.splitlines())
fixed=sum(bool(re.match(r'^FAIL:.*repeats',line)) for line in out.splitlines())
assert fixed==0, fixed
workflow=Path('kc-dev-flow-2/references/sd/workflow.md').read_text()
assert 'Every criterion' in workflow and 'per criterion, provenance included' in workflow
assert 'writes no repository file' not in Path('kc-dev-flow-2/skills/ideation/principles.md').read_text()
assert 'ideation writes no repository file' not in Path('kc-dev-flow-2/scripts/lint-skills.py').read_text()
print('STEP 4 PASS: corrected failure pattern 0; per-criterion provenance wording present')
PY4
echo 'LIMIT: no UI; this script checks package text and regressions, not another model run, third-dispatch enforcement, post-release cleanup, or delivery.'
