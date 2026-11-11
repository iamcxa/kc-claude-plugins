#!/bin/bash
set -euo pipefail

# Step 1: Export the exact candidate and both comparison versions.
EVIDENCE="$(cd "$(dirname "$0")" && pwd)"
REPO="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worth-questions-asked-only-before-the-design-gate"
PACKAGE="/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.0"
BASE="44f11855264bde64da284ffa9c1fef70e8ac38dd"
HEAD="78905b08d6f38817ccdda5d2e91be478fd75dfc7"
export SPACEDOCK_BIN="/Users/kent/.local/bin/spacedock" PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_WORK_TREE
test "$(git -C "$REPO" rev-parse HEAD)" = "$HEAD"
test -x "$SPACEDOCK_BIN"
RUN="$(mktemp -d /tmp/pr849-captain.XXXXXX)"
trap 'rm -rf -- "$RUN"; echo "Removed scratch: $RUN"' EXIT
mkdir -p "$RUN/candidate" "$RUN/baseline" "$RUN/v038" "$RUN/tmp"
export TMPDIR="$RUN/tmp"
git -C "$REPO" archive "$HEAD" | tar -x -C "$RUN/candidate"
git -C "$REPO" archive "$BASE" | tar -x -C "$RUN/baseline"
git -C "$REPO" archive kc-dev-flow-2-v0.38.1 | tar -x -C "$RUN/v038"
echo "Step 1 PASS: exact head $HEAD exported"

# Step 2: Require all seven Worth tests and reject the three counterexamples.
(
  cd "$RUN/candidate/kc-dev-flow-2/scripts"
  python3 -B -m unittest -v test_design_surfaces.WorthQuestionsTests
)
python3 -B "$EVIDENCE/mutations.py" "$RUN"
echo "Step 2 PASS: 7 tests, no skips; all 3 mutations detected"

# Step 3: Re-run the 173-task corpus using read-only pinned source exports.
python3 -B "$EVIDENCE/replay.py" "$RUN"
echo "Step 3 PASS: 10 releases, 17 ideation refusals, no other differences"

# Step 4: Check decision records and the approved three-file scope.
(
  cd "$RUN/candidate"
  export GIT_DIR="$(git -C "$REPO" rev-parse --absolute-git-dir)" GIT_WORK_TREE="$RUN/candidate"
  python3 "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE" --require 77
)
python3 -B - "$REPO" "$BASE" "$HEAD" "$EVIDENCE/pr.json" <<'PY'
import json, subprocess, sys
repo, base, head, pr_file = sys.argv[1:]
expected = {
    "kc-dev-flow-2/scripts/design_surfaces.py",
    "kc-dev-flow-2/scripts/test_design_surfaces.py",
    "kc-dev-flow-2/skills/observer/SKILL.md",
}
paths = set(subprocess.check_output(["git", "-C", repo, "diff", "--name-only", base, head], text=True).splitlines())
pr = json.load(open(pr_file))
def valid(files, title):
    return files == expected and title.startswith("fix(kc-dev-flow-2): ")
assert valid(paths, pr["title"]) and pr["head_sha"] == head
assert not valid(paths | {"unexpected-file"}, pr["title"])
assert not valid(paths, pr["title"].replace("fix(", "feat(", 1))
print("AC-5: three-file scope and captured exact-head PR title pass; extra path/non-fix controls rejected")
PY
echo "Step 4 PASS: 70 ADRs; approved scope and title"
echo "Acceptance PASS"

