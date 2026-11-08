#!/usr/bin/env bash
set -euo pipefail
# Dependencies: Python 3.11+, bash, git, tar, and the exact local paths below.
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-adr-lint-tells-supersession-assertion-from-pointer
WORKFLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
TASK="$WORKFLOW/.spacedock-state/adr-lint-tells-supersession-assertion-from-pointer.md"
TASKDIR="${TASK%.md}"
PACKAGE=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0
SD_PLUGIN=/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.3
BASE=139feeaee7ce037a0c6535568cd6bd103155cbae
HEAD_SHA=f429f0fac40511c6480fd92e2cccd4c0e94b2454
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$(mktemp -d /tmp/adr806-acceptance.XXXXXX)"
mkdir -p "$RUN/candidate" "$RUN/results"
export PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
RESULTS="$RUN/results"
run_check() {
  local name="$1" expected="$2" actual=0
  shift 2
  "$@" > "$RESULTS/$name.log" 2>&1 || actual=$?
  printf '%s\t%s\t%s\n' "$name" "$actual" "$expected" >> "$RESULTS/exits.tsv"
  printf '%s: exit %s (expected %s)\n' "$name" "$actual" "$expected"
  if [[ "$actual" != "$expected" ]]; then
    cat "$RESULTS/$name.log"
    return 1
  fi
}

# Step 1 — Export the exact candidate; expect the named SHA and four changed files.
test "$(git -C "$REPO" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$REPO" archive "$HEAD_SHA" | tar -x -C "$RUN/candidate"
GIT_METADATA="$(git -C "$REPO" rev-parse --absolute-git-dir)"
git -C "$REPO" diff --name-only "$BASE" "$HEAD_SHA" > "$RESULTS/changed-files.txt"
git -C "$REPO" diff "$BASE" "$HEAD_SHA" > "$RESULTS/candidate.diff"
for path in kc-adr/scripts/adr_lint.py kc-adr/scripts/test_adr_lint.py kc-dev-flow-2/scripts/adr_lint.py kc-dev-flow-2/scripts/test_sd_dispatch.py; do
  cmp "$REPO/$path" "$RUN/candidate/$path"
done
cd "$RUN/candidate"
printf 'Step 1: exported %s\n' "$HEAD_SHA"

# Step 2 — Run the three required suites and parity; expect exits 0, 25 tests, 9 tests and native integration success.
run_check adr-tests 0 python3 -B kc-adr/scripts/test_adr_lint.py
run_check doc-tests 0 python3 -B kc-dev-flow-2/scripts/test_adr_doc_checks.py
run_check native-dispatch 0 python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root "$SD_PLUGIN"
run_check copy-sync 0 bash scripts/kc-adr-copy-sync.sh check

# Step 3 — Replay the real unsplit citation; candidate exits 0; installed checker exits 1 with the known 0047/0050 message.
run_check candidate-full 0 python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr
run_check candidate-since 0 env GIT_OPTIONAL_LOCKS=0 GIT_DIR="$GIT_METADATA" GIT_WORK_TREE="$RUN/candidate" python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since "$BASE" --require 0064
run_check installed-since 1 env GIT_OPTIONAL_LOCKS=0 GIT_DIR="$GIT_METADATA" GIT_WORK_TREE="$RUN/candidate" python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE"
grep -F 'kc-dev-flow-2/scripts/test_sd_dispatch.py: points at ADR 0047, Superseded by 0050; point it at 0050 or the record in force' "$RESULTS/installed-since.log"
git -C "$REPO" show "$BASE:kc-dev-flow-2/scripts/adr_lint.py" > "$RESULTS/base-checker.py"
cmp "$RESULTS/base-checker.py" "$PACKAGE/scripts/adr_lint.py"
shasum -a 256 kc-adr/scripts/adr_lint.py kc-dev-flow-2/scripts/adr_lint.py "$PACKAGE/scripts/adr_lint.py" > "$RESULTS/checker-sha256.txt"

# Step 4 — Reuse the implementation's mutation/history proof; expect all 11 outcomes to match, including negative exits 1.
# prove.py only reads REPO, creates archive exports under /tmp, and mutates those exports.
run_check mutations-history 0 python3 -B "$TASKDIR/implementation/prove.py" "$REPO" "$RESULTS/proof"
run_check limits 0 python3 -B "$HERE/limits.py" "$RUN/candidate" "$RESULTS/limits.json"

# Step 5 — Check workflow obligations; expect all exits 0, no doc dispositions missing, and no candidate changes.
run_check lint-skills 0 python3 -B kc-dev-flow-2/scripts/lint-skills.py
run_check design-surfaces 0 python3 -B "$PACKAGE/scripts/design_surfaces.py" check "$TASK"
run_check number-guards 0 env GIT_OPTIONAL_LOCKS=0 GIT_DIR="$GIT_METADATA" GIT_WORK_TREE="$RUN/candidate" python3 -B "$PACKAGE/scripts/number_guards.py" check --workflow-dir "$WORKFLOW" --task "$TASK" --base "$BASE"
run_check comment-ratio 0 env GIT_OPTIONAL_LOCKS=0 GIT_DIR="$GIT_METADATA" GIT_WORK_TREE="$RUN/candidate" python3 -B "$PACKAGE/scripts/comment_ratio.py" "$BASE" "$HEAD_SHA" --workflow-dir "$WORKFLOW"
run_check doc-impact 0 env GIT_OPTIONAL_LOCKS=0 GIT_DIR="$GIT_METADATA" GIT_WORK_TREE="$RUN/candidate" python3 -B "$PACKAGE/scripts/doc_impact.py" "$BASE" "$HEAD_SHA" --json
run_check dispatch-records 0 python3 -B "$PACKAGE/scripts/dispatch_records.py" "$TASKDIR"
run_check diff-whitespace 0 git -C "$REPO" diff --check "$BASE" "$HEAD_SHA"
test "$(git -C "$REPO" rev-parse HEAD)" = "$HEAD_SHA"
test -z "$(git -C "$REPO" status --porcelain)"
python3 -B - "$RESULTS" "$HEAD_SHA" "$BASE" <<'PY'
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
rows = []
for line in (out / 'exits.tsv').read_text().splitlines():
    name, actual, expected = line.split('\t')
    rows.append({'name': name, 'status': 'passed' if actual == expected else 'failed',
                 'message': f'exit {actual}, expected {expected}', 'file': str(out / (name + '.log'))})
(out / 'tests.json').write_text(json.dumps(rows, indent=2) + '\n')
(out / 'receipt.json').write_text(json.dumps({'candidate': sys.argv[2], 'base': sys.argv[3],
    'candidate_unchanged': True, 'installed_checker_matches_base': True,
    'installed_check_acceptance': 'SKIPPED per FO; independently reproduced exit 1',
    'limits': ['Same-line textual rule; no semantic assertion parsing.',
               'Local export evidence; no hosted CI, RoboRev, merge or release claim.']}, indent=2) + '\n')
PY
printf 'PASS: all expected outcomes; evidence: %s\n' "$RESULTS"
